#Heavily influenced by https://github.com/facebookresearch/audiocraft/blob/main/audiocraft/modules/conditioners.py

import torch
import logging, warnings
import math
import string
import typing as tp
import gc
import numpy as np

from .adp import NumberEmbedder
from ..inference.utils import set_audio_channels
from .factory import create_pretransform_from_config
from .pretransforms import Pretransform
from .utils import load_ckpt_state_dict
from .transformer import AbsolutePositionalEmbedding

from torch import nn

class Conditioner(nn.Module):
    def __init__(
            self,
            dim: int,
            output_dim: int,
            project_out: bool = False
            ):

        super().__init__()

        self.dim = dim
        self.output_dim = output_dim
        self.proj_out = nn.Linear(dim, output_dim) if (dim != output_dim or project_out) else nn.Identity()

    def forward(self, x: tp.Any) -> tp.Any:
        raise NotImplementedError()

class IntConditioner(Conditioner):
    def __init__(self,
                output_dim: int,
                min_val: int=0,
                max_val: int=512
                ):
        super().__init__(output_dim, output_dim)

        self.min_val = min_val
        self.max_val = max_val
        self.int_embedder = nn.Embedding(max_val - min_val + 1, output_dim).requires_grad_(True)

    def forward(self, ints: tp.List[int], device=None) -> tp.Any:

            #self.int_embedder.to(device)

            ints = torch.tensor(ints).to(device)
            ints = ints.clamp(self.min_val, self.max_val)

            int_embeds = self.int_embedder(ints).unsqueeze(1)

            return [int_embeds, torch.ones(int_embeds.shape[0], 1).to(device)]

class NumberConditioner(Conditioner):
    '''
        Conditioner that takes a list of floats, normalizes them for a given range, and returns a list of embeddings
    '''
    def __init__(self,
                output_dim: int,
                min_val: float=0,
                max_val: float=1
                ):
        super().__init__(output_dim, output_dim)

        self.min_val = min_val
        self.max_val = max_val

        self.embedder = NumberEmbedder(features=output_dim)

    def forward(self, floats: tp.List[float], device=None) -> tp.Any:

            # Cast the inputs to floats
            floats = [float(x) for x in floats]

            floats = torch.tensor(floats).to(device)

            floats = floats.clamp(self.min_val, self.max_val)

            normalized_floats = (floats - self.min_val) / (self.max_val - self.min_val)

            # Cast floats to same type as embedder
            embedder_dtype = next(self.embedder.parameters()).dtype
            normalized_floats = normalized_floats.to(embedder_dtype)

            float_embeds = self.embedder(normalized_floats).unsqueeze(1)

            return [float_embeds, torch.ones(float_embeds.shape[0], 1).to(device)]

class ListConditioner(Conditioner):
    def __init__(self,
                output_dim: int,
                options: tp.List[str]
                ):
        super().__init__(output_dim, output_dim)

        self.options = options
        self.embedder = nn.Embedding(len(options)+1, output_dim).requires_grad_(True)

    def forward(self, texts: tp.List[str], device=None) -> tp.Any:

        # Cast the inputs to floats, handling the case where the input is not in the options
        ints = [self.options.index(x) + 1 if x in self.options else 0 for x in texts]

        ints = torch.tensor(ints).to(device) # shape [batch_size]

        int_embeds = self.embedder(ints).unsqueeze(1) # shape [batch_size, 1, output_dim]

        return [int_embeds, torch.ones(int_embeds.shape[0], 1).to(device)]

class PositionConditioner(Conditioner):
    """
        Conditioner for parametric spatial baselines.
        Input is a 6D vector: [az_start, az_end, el_start, el_end, r_start, r_end].
    """
    def __init__(
            self,
            output_dim: int,
            input_dim: int = 6,
            hidden_dim: int = 768,
            dropout: float = 0.0
            ):
        super().__init__(output_dim, output_dim)

        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, positions: tp.List[tp.Any], device=None) -> tp.Any:
        position_tensor = torch.as_tensor(np.asarray(positions), dtype=torch.float32, device=device)
        if position_tensor.ndim == 1:
            position_tensor = position_tensor.unsqueeze(0)
        embeds = self.net(position_tensor).unsqueeze(1)
        return [embeds, torch.ones(embeds.shape[0], 1).to(device)]

def clap_load_state_dict(clap_ckpt_path, clap_model):
    state_dict = torch.load(clap_ckpt_path, map_location="cpu", weights_only=False)["state_dict"]

    # Remove "module." from state dict keys
    state_dict = {k[7:]: v for k, v in state_dict.items()}

    # Fix for transformers library
    removed_keys = ["text_branch.embeddings.position_ids"]
    for removed_key in removed_keys:
        if removed_key in state_dict:
            del state_dict[removed_key]

    clap_model.load_state_dict(state_dict, strict=False)

class CLAPTextConditioner(Conditioner):
    def __init__(self,
                 output_dim: int,
                 clap_ckpt_path,
                 use_text_features = False,
                 feature_layer_ix: int = -1,
                 audio_model_type="HTSAT-base",
                 enable_fusion=True,
                 project_out: bool = False,
                 finetune: bool = False):
        super().__init__(768 if use_text_features else 512, output_dim, project_out=project_out)

        self.use_text_features = use_text_features
        self.feature_layer_ix = feature_layer_ix
        self.finetune = finetune

        # Suppress logging from transformers
        previous_level = logging.root.manager.disable
        logging.disable(logging.ERROR)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                import laion_clap

                model = laion_clap.CLAP_Module(enable_fusion=enable_fusion, amodel=audio_model_type, device='cpu')

                if self.finetune:
                    self.model = model
                else:
                    self.__dict__["model"] = model

                clap_load_state_dict(clap_ckpt_path, self.model.model)

                if self.finetune:
                    self.model.model.text_branch.requires_grad_(True)
                    self.model.model.text_branch.train()
                else:
                    self.model.model.text_branch.requires_grad_(False)
                    self.model.model.text_branch.eval()

            finally:
                logging.disable(previous_level)

        del self.model.model.audio_branch

        gc.collect()
        torch.cuda.empty_cache()

    def get_clap_features(self, prompts, layer_ix=-2, device: tp.Any = "cuda"):
        prompt_tokens = self.model.tokenizer(prompts)
        attention_mask = prompt_tokens["attention_mask"].to(device=device, non_blocking=True)
        prompt_features = self.model.model.text_branch(
            input_ids=prompt_tokens["input_ids"].to(device=device, non_blocking=True),
            attention_mask=attention_mask,
            output_hidden_states=True
        )["hidden_states"][layer_ix]

        return prompt_features, attention_mask

    def forward(self, texts: tp.List[str], device: tp.Any = "cuda") -> tp.Any:
        self.model.to(device)

        if self.use_text_features:
            if len(texts) == 1:
                text_features, text_attention_mask = self.get_clap_features([texts[0], ""], layer_ix=self.feature_layer_ix, device=device)
                text_features = text_features[:1, ...]
                text_attention_mask = text_attention_mask[:1, ...]
            else:
                text_features, text_attention_mask = self.get_clap_features(texts, layer_ix=self.feature_layer_ix, device=device)

            # Cast text feature to same type as proj_out, unless proj_out is Identity
            if not isinstance(self.proj_out, nn.Identity):
                proj_out_dtype = next(self.proj_out.parameters()).dtype
                text_features = text_features.to(proj_out_dtype)

            return [self.proj_out(text_features), text_attention_mask]

        # Fix for CLAP bug when only one text is passed
        if len(texts) == 1:
            text_embedding = self.model.get_text_embedding([texts[0], ""], use_tensor=True)[:1, ...]
        else:
            text_embedding = self.model.get_text_embedding(texts, use_tensor=True)

        text_embedding = text_embedding.unsqueeze(1).to(device)

        # Cast text embedding to same type as proj_out, unless proj_out is Identity
        if not isinstance(self.proj_out, nn.Identity):
            proj_out_dtype = next(self.proj_out.parameters()).dtype
            text_embedding = text_embedding.to(proj_out_dtype)

        return [self.proj_out(text_embedding), torch.ones(text_embedding.shape[0], 1).to(device)]

class CLAPAudioConditioner(Conditioner):
    def __init__(self,
                 output_dim: int,
                 clap_ckpt_path,
                 audio_model_type="HTSAT-base",
                 enable_fusion=True,
                 project_out: bool = False):
        super().__init__(512, output_dim, project_out=project_out)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Suppress logging from transformers
        previous_level = logging.root.manager.disable
        logging.disable(logging.ERROR)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                import laion_clap

                model = laion_clap.CLAP_Module(enable_fusion=enable_fusion, amodel=audio_model_type, device='cpu')

                if self.finetune:
                    self.model = model
                else:
                    self.__dict__["model"] = model

                clap_load_state_dict(clap_ckpt_path, self.model.model)

                if self.finetune:
                    self.model.model.audio_branch.requires_grad_(True)
                    self.model.model.audio_branch.train()
                else:
                    self.model.model.audio_branch.requires_grad_(False)
                    self.model.model.audio_branch.eval()

            finally:
                logging.disable(previous_level)

        del self.model.model.text_branch

        gc.collect()
        torch.cuda.empty_cache()

    def forward(self, audios: tp.Union[torch.Tensor, tp.List[torch.Tensor], tp.Tuple[torch.Tensor]] , device: tp.Any = "cuda") -> tp.Any:

        self.model.to(device)

        if isinstance(audios, list) or isinstance(audios, tuple):
            audios = torch.cat(audios, dim=0)

        # Convert to mono
        mono_audios = audios.mean(dim=1)

        with torch.cuda.amp.autocast(enabled=False):
            audio_embedding = self.model.get_audio_embedding_from_data(mono_audios.float(), use_tensor=True)

        audio_embedding = audio_embedding.unsqueeze(1).to(device)

        # Cast audio embedding to same type as proj_out, unless proj_out is Identity

        if not isinstance(self.proj_out, nn.Identity):
            proj_out_dtype = next(self.proj_out.parameters()).dtype
            audio_embedding = audio_embedding.to(proj_out_dtype)

        return [self.proj_out(audio_embedding), torch.ones(audio_embedding.shape[0], 1).to(device)]

class CLAPConditioner(Conditioner):
    """
    Unified CLAP conditioner that holds a single CLAP model with both text and
    audio branches. Dispatches by input type at forward time:
      - List[str] -> text branch (used at inference)
      - List[Tensor] / Tensor of waveforms -> audio branch (used at training)

    AudioLDM-style training tricks applied during training only:
      - Gaussian noise added to embedding (noise_std)
      - Random text-mix: when a batch of audios is given alongside captions,
        with text_mix_prob switch the whole batch to text branch
      - Unconditional dropout: with cond_dropout, zero-out the embedding
        (CFG-friendly null embedding)

    Output shape: (B, 1, output_dim).
    """

    def __init__(
        self,
        output_dim: int,
        clap_ckpt_path,
        audio_model_type: str = "HTSAT-tiny",
        enable_fusion: bool = True,
        audio_sample_rate: int = 48000,
        text_mix_prob: float = 0.0,
        cond_dropout: float = 0.0,
        project_out: bool = False,
    ):
        super().__init__(512, output_dim, project_out=project_out)

        self.audio_sample_rate = audio_sample_rate
        self.text_mix_prob = text_mix_prob
        self.cond_dropout = cond_dropout

        previous_level = logging.root.manager.disable
        logging.disable(logging.ERROR)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                import laion_clap
                model = laion_clap.CLAP_Module(
                    enable_fusion=enable_fusion,
                    amodel=audio_model_type,
                    device="cpu",
                )
                # Keep CLAP frozen and outside the parameter tree
                self.__dict__["model"] = model
                clap_load_state_dict(clap_ckpt_path, self.model.model)
                self.model.model.text_branch.requires_grad_(False)
                self.model.model.text_branch.eval()
                self.model.model.audio_branch.requires_grad_(False)
                self.model.model.audio_branch.eval()
            finally:
                logging.disable(previous_level)

        gc.collect()
        torch.cuda.empty_cache()

    def _embed_text(self, texts: tp.List[str]) -> torch.Tensor:
        if len(texts) == 1:
            emb = self.model.get_text_embedding([texts[0], ""], use_tensor=True)[:1, ...]
        else:
            emb = self.model.get_text_embedding(texts, use_tensor=True)
        return emb  # (B, 512)

    def _embed_audio(self, audios) -> torch.Tensor:
        if isinstance(audios, (list, tuple)):
            audios = torch.stack([a if a.ndim == 1 else a.mean(dim=0) for a in audios], dim=0)
        elif audios.ndim == 3:
            audios = audios.mean(dim=1)
        # audios: (B, T) at self.audio_sample_rate (expected 48kHz)
        with torch.cuda.amp.autocast(enabled=False):
            emb = self.model.get_audio_embedding_from_data(audios.float(), use_tensor=True)
        return emb  # (B, 512)

    def forward(self, inputs, device: tp.Any = "cuda") -> tp.Any:
        self.model.to(device)

        is_text = isinstance(inputs, list) and len(inputs) > 0 and isinstance(inputs[0], str)

        if self.training and is_text is False and self.text_mix_prob > 0.0:
            # Caller passed audio, but we don't have captions here at the
            # conditioner level. Text-mix is handled by the dataset/wrapper:
            # see CLAPConditioner usage notes — when text-mix fires the caller
            # passes List[str] instead of audio.
            pass

        if is_text:
            embedding = self._embed_text(inputs)
        else:
            if isinstance(inputs, list):
                # Could be list of 1-D tensors or list of (1,T) tensors
                tensors = []
                for a in inputs:
                    if not torch.is_tensor(a):
                        a = torch.as_tensor(a)
                    a = a.to(device)
                    if a.ndim == 2:
                        a = a.mean(dim=0)
                    tensors.append(a)
                # Pad/truncate to common length
                T = max(t.shape[-1] for t in tensors)
                tensors = [
                    torch.nn.functional.pad(t, (0, T - t.shape[-1])) if t.shape[-1] < T else t[:T]
                    for t in tensors
                ]
                audios = torch.stack(tensors, dim=0)
            else:
                audios = inputs.to(device)
            embedding = self._embed_audio(audios)

        embedding = embedding.to(device)

        # CFG-style unconditional dropout (training only)
        if self.training and self.cond_dropout > 0.0:
            mask = (torch.rand(embedding.shape[0], 1, device=device) >= self.cond_dropout).float()
            embedding = embedding * mask

        embedding = embedding.unsqueeze(1)  # (B, 1, 512)

        if not isinstance(self.proj_out, nn.Identity):
            proj_out_dtype = next(self.proj_out.parameters()).dtype
            embedding = embedding.to(proj_out_dtype)

        return [self.proj_out(embedding), torch.ones(embedding.shape[0], 1).to(device)]


class T5Conditioner(Conditioner):

    T5_MODELS = ["t5-small", "t5-base", "t5-large", "t5-3b", "t5-11b",
              "google/flan-t5-small", "google/flan-t5-base", "google/flan-t5-large",
              "google/flan-t5-xl", "google/flan-t5-xxl", "google/t5-v1_1-xl", "google/t5-v1_1-xxl"]

    T5_MODEL_DIMS = {
        "t5-small": 512,
        "t5-base": 768,
        "t5-large": 1024,
        "t5-3b": 1024,
        "t5-11b": 1024,
        "google/t5-v1_1-xl": 2048,
        "google/t5-v1_1-xxl": 4096,
        "google/flan-t5-small": 512,
        "google/flan-t5-base": 768,
        "google/flan-t5-large": 1024,
        "google/flan-t5-3b": 1024,
        "google/flan-t5-11b": 1024,
        "google/flan-t5-xl": 2048,
        "google/flan-t5-xxl": 4096,
    }

    def __init__(
            self,
            output_dim: int,
            t5_model_name: str = "t5-base",
            max_length: str = 128,
            enable_grad: bool = False,
            project_out: bool = False
    ):
        assert t5_model_name in self.T5_MODELS, f"Unknown T5 model name: {t5_model_name}"
        super().__init__(self.T5_MODEL_DIMS[t5_model_name], output_dim, project_out=project_out)

        from transformers import T5EncoderModel, AutoTokenizer

        self.max_length = max_length
        self.enable_grad = enable_grad

        # Suppress logging from transformers
        previous_level = logging.root.manager.disable
        logging.disable(logging.ERROR)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                # self.tokenizer = T5Tokenizer.from_pretrained(t5_model_name, model_max_length = max_length)
                # model = T5EncoderModel.from_pretrained(t5_model_name, max_length=max_length).train(enable_grad).requires_grad_(enable_grad)
                self.tokenizer = AutoTokenizer.from_pretrained(t5_model_name)
                model = T5EncoderModel.from_pretrained(t5_model_name).train(enable_grad).requires_grad_(enable_grad)
            finally:
                logging.disable(previous_level)

        if self.enable_grad:
            self.model = model
        else:
            self.__dict__["model"] = model


    def forward(self, texts: tp.List[str], device: tp.Union[torch.device, str]) -> tp.Tuple[torch.Tensor, torch.Tensor]:

        self.model.to(device)
        self.proj_out.to(device)

        encoded = self.tokenizer(
            texts,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded["attention_mask"].to(device).to(torch.bool)

        self.model.eval()

        device_type = torch.device(device).type
        with torch.amp.autocast(device_type=device_type, enabled=False):
            with torch.set_grad_enabled(self.enable_grad):
                embeddings = self.model(
                    input_ids=input_ids, attention_mask=attention_mask
                )["last_hidden_state"]

        # Cast embeddings to same type as proj_out, unless proj_out is Identity
        if not isinstance(self.proj_out, nn.Identity):
            proj_out_dtype = next(self.proj_out.parameters()).dtype
            embeddings = embeddings.to(proj_out_dtype)

        embeddings = self.proj_out(embeddings)

        embeddings = embeddings * attention_mask.unsqueeze(-1).float()

        return embeddings, attention_mask

class PhonemeConditioner(Conditioner):
    """
    A conditioner that turns text into phonemes and embeds them using a lookup table
    Only works for English text

    Args:
        output_dim: the dimension of the output embeddings
        max_length: the maximum number of phonemes to embed
        project_out: whether to add another linear projection to the output embeddings
    """

    def __init__(
            self,
            output_dim: int,
            max_length: int = 1024,
            project_out: bool = False,
    ):
        super().__init__(output_dim, output_dim, project_out=project_out)

        from g2p_en import G2p

        self.max_length = max_length

        self.g2p = G2p()

        # Reserving 0 for padding, 1 for ignored
        self.phoneme_embedder = nn.Embedding(len(self.g2p.phonemes) + 2, output_dim)

    def forward(self, texts: tp.List[str], device: tp.Union[torch.device, str]) -> tp.Tuple[torch.Tensor, torch.Tensor]:

        self.phoneme_embedder.to(device)
        self.proj_out.to(device)

        batch_phonemes = [self.g2p(text) for text in texts] # shape [batch_size, length]

        phoneme_ignore = [" ", *string.punctuation]

        # Remove ignored phonemes and cut to max length
        batch_phonemes = [[p if p not in phoneme_ignore else "_" for p in phonemes] for phonemes in batch_phonemes]

        # Convert to ids
        phoneme_ids = [[self.g2p.p2idx[p] + 2 if p in self.g2p.p2idx else 1 for p in phonemes] for phonemes in batch_phonemes]

        #Pad to match longest and make a mask tensor for the padding
        longest = max([len(ids) for ids in phoneme_ids])
        phoneme_ids = [ids + [0] * (longest - len(ids)) for ids in phoneme_ids]

        phoneme_ids = torch.tensor(phoneme_ids).to(device)

        # Convert to embeddings
        phoneme_embeds = self.phoneme_embedder(phoneme_ids)

        phoneme_embeds = self.proj_out(phoneme_embeds)

        return phoneme_embeds, torch.ones(phoneme_embeds.shape[0], phoneme_embeds.shape[1]).to(device)

class TokenizerLUTConditioner(Conditioner):
    """
    A conditioner that embeds text using a lookup table on a pretrained tokenizer's vocabulary

    Args:
        tokenizer_name: the name of the tokenizer from the Hugging Face transformers library
        output_dim: the dimension of the output embeddings
        max_length: the maximum length of the text to embed
        project_out: whether to add another linear projection to the output embeddings
    """

    def __init__(
            self,
            tokenizer_name: str, # Name of a tokenizer from the Hugging Face transformers library
            output_dim: int,
            max_length: int = 1024,
            use_abs_pos_emb = False,
            project_out: bool = False,
            special_tokens: tp.List[str] = []
    ):
        super().__init__(output_dim, output_dim, project_out=project_out)

        from transformers import AutoTokenizer

         # Suppress logging from transformers
        previous_level = logging.root.manager.disable
        logging.disable(logging.ERROR)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
            finally:
                logging.disable(previous_level)

        # Add special tokens
        if len(special_tokens) > 0:
            self.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

        self.max_length = max_length

        self.token_embedder = nn.Embedding(len(self.tokenizer), output_dim)

        self.abs_pos_emb = None

        if use_abs_pos_emb:
            self.abs_pos_emb = AbsolutePositionalEmbedding(output_dim, max_length)

    def forward(self, texts: tp.List[str], device: tp.Union[torch.device, str]) -> tp.Tuple[torch.Tensor, torch.Tensor]:
        self.proj_out.to(device)

        encoded = self.tokenizer(
            texts,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded["attention_mask"].to(device).to(torch.bool)

        embeddings = self.token_embedder(input_ids)

        embeddings = self.proj_out(embeddings)

        embeddings = embeddings * attention_mask.unsqueeze(-1).float()

        if self.abs_pos_emb is not None:
            embeddings = embeddings + self.abs_pos_emb(embeddings)

        return embeddings, attention_mask

class PretransformConditioner(Conditioner):
    """
    A conditioner that uses a pretransform's encoder for conditioning

    Args:
        pretransform: an instantiated pretransform to use for conditioning
        output_dim: the dimension of the output embeddings
    """
    def __init__(self, pretransform: Pretransform, output_dim: int, save_pretransform: bool = False):
        super().__init__(pretransform.encoded_channels, output_dim)


        if not save_pretransform:
            self.__dict__["pretransform"] = pretransform
        else:
            self.pretransform = pretransform


    def forward(self, audio: tp.Union[torch.Tensor, tp.List[torch.Tensor], tp.Tuple[torch.Tensor]], device: tp.Union[torch.device, str]) -> tp.Tuple[torch.Tensor, torch.Tensor]:

        self.pretransform.to(device)
        self.proj_out.to(device)

        if isinstance(audio, list) or isinstance(audio, tuple):
            audio = torch.stack(audio, dim=0)

        # Add batch dimension if needed
        if audio.dim() == 2:
            audio = audio.unsqueeze(0)

        # Convert audio to pretransform input channels
        audio = set_audio_channels(audio, self.pretransform.io_channels)

        audio = audio.to(device)

        latents = self.pretransform.encode(audio)

        latents = self.proj_out(latents)

        return [latents, torch.ones(latents.shape[0], latents.shape[2]).to(latents.device)]

class SourceMixConditioner(Conditioner):
    """
    A conditioner that mixes projected audio embeddings from multiple sources

    Args:
        pretransform: an instantiated pretransform to use for conditioning
        output_dim: the dimension of the output embeddings
        source_keys: a list of keys for the potential sources in the metadata

    """
    def __init__(
        self,
        pretransform: Pretransform,
        output_dim: int,
        save_pretransform: bool = False,
        source_keys: tp.List[str] = [],
        pre_encoded: bool = False,
        allow_null_source=False,
        source_length=None
    ):
        super().__init__(pretransform.encoded_channels, output_dim)

        if not save_pretransform:
            self.__dict__["pretransform"] = pretransform
        else:
            self.pretransform = pretransform

        self.source_keys = source_keys

        self.source_heads = nn.ModuleList([nn.Conv1d(pretransform.encoded_channels, output_dim, kernel_size=1) for _ in source_keys])

        self.pre_encoded = pre_encoded

        self.allow_null_source = allow_null_source

        if self.allow_null_source:
            self.null_source = nn.Parameter(torch.randn(output_dim, 1))

            assert source_length is not None, "Source length must be specified if allowing null sources"

            self.source_length = source_length

    def forward(self, sources: tp.List[tp.Dict[str, torch.Tensor]], device: tp.Union[torch.device, str]) -> tp.Tuple[torch.Tensor, torch.Tensor]:

        self.pretransform.to(device)
        self.proj_out.to(device)

        dtype = next(self.proj_out.parameters()).dtype

        # Output has to be the batch of summed projections
        # Input is per-batch-item list of source audio

        mixes = []

        for source_dict in sources: # Iterate over batch items

            mix = None

            for key_ix, key in enumerate(self.source_keys): # Iterate over potential sources
                if key in source_dict:

                    source = source_dict[key]

                    if not self.pre_encoded:
                        assert source.dim() == 2, f"Source audio must be shape [channels, samples], got shape: {source.shape}"
                        audio = set_audio_channels(source.unsqueeze(0), self.pretransform.io_channels)

                        audio = audio.to(device)
                        latents = self.pretransform.encode(audio).squeeze(0)
                    else:
                        latents = source.to(device)

                    latents = latents.to(dtype)

                    if mix is None:
                        mix = self.source_heads[key_ix](latents)
                    else:
                        mix += self.source_heads[key_ix](latents)

            if mix is not None:
                mixes.append(mix)
            else:
                if self.allow_null_source:
                    mixes.append(self.null_source.repeat(1, self.source_length))
                else:
                    raise ValueError("No sources found for mix")

        mixes = torch.stack(mixes, dim=0)

        return [mixes, torch.ones(mixes.shape[0], mixes.shape[2]).to(mixes.device)]


class WaypointConditionerLegacy(Conditioner):
    """
    [LEGACY — backup of the cross-attention waypoint conditioner.]

    Encodes a spatial trajectory — represented as N waypoints of
    [t, azimuth_deg, elevation_deg, distance_m] — into a sequence of
    cross-attention tokens that the diffusion transformer can attend to.

    Each waypoint is independently projected to output_dim, then passed
    through a small Transformer encoder so that the model can learn
    relationships between waypoints (e.g. direction of motion, speed).

    The input to forward() is a list (length B) of numpy arrays or tensors
    of shape (N, 4).  All items are resampled to exactly `n_waypoints`
    points via linear interpolation so the sequence length is fixed.

    Normalisation (per-channel, to roughly [-1, 1]):
        t           : divided by max_duration
        azimuth     : divided by 180
        elevation   : divided by 90
        distance    : log1p(d) / log1p(max_dist)
    """

    def __init__(
        self,
        output_dim: int,
        n_waypoints: int = 10,
        d_model: int = 256,
        n_heads: int = 4,
        n_layers: int = 2,
        max_duration: float = 10.0,
        max_dist: float = 50.0,
        dropout: float = 0.1,
    ):
        # input dim = 4 (raw waypoint), we project internally
        super().__init__(d_model, output_dim, project_out=(d_model != output_dim))

        self.n_waypoints = n_waypoints
        self.max_duration = max_duration
        self.max_dist = max_dist

        # Project each waypoint (4 dims) → d_model
        self.input_proj = nn.Linear(4, d_model)

        # Learned positional embedding for the N waypoint positions
        self.pos_embed = nn.Embedding(n_waypoints, d_model)

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True,
            norm_first=True,          # pre-norm, more stable
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

    def _resample(self, wp: torch.Tensor) -> torch.Tensor:
        """
        Linearly resample waypoints to exactly self.n_waypoints points.
        wp: (N_orig, 4)  →  (n_waypoints, 4)
        """
        N = wp.shape[0]
        if N == self.n_waypoints:
            return wp
        # Use t column (col 0) as the time axis for interpolation
        t_orig = wp[:, 0]
        t_new  = torch.linspace(t_orig[0], t_orig[-1], self.n_waypoints,
                                device=wp.device, dtype=wp.dtype)
        out = torch.zeros(self.n_waypoints, 4, device=wp.device, dtype=wp.dtype)
        for dim in range(4):
            out[:, dim] = torch.from_numpy(
                __import__('numpy').interp(
                    t_new.cpu().numpy(),
                    t_orig.cpu().numpy(),
                    wp[:, dim].cpu().numpy(),
                )
            ).to(wp.device, wp.dtype)
        return out

    def _normalise(self, wp: torch.Tensor) -> torch.Tensor:
        """
        Normalise (n_waypoints, 4) to roughly [-1, 1] per channel.
        Columns: [t, az, el, dist]
        """
        t   = wp[:, 0] / self.max_duration                           # [0, 1]
        az  = wp[:, 1] / 180.0                                       # [-1, 1]
        el  = wp[:, 2] / 90.0                                        # [-1, 1]
        dist = torch.log1p(wp[:, 3].clamp(min=0)) / \
               torch.log1p(torch.tensor(self.max_dist,
                                        device=wp.device, dtype=wp.dtype))
        return torch.stack([t, az, el, dist], dim=1)                 # (N, 4)

    def forward(
        self,
        waypoints: tp.List,          # list of (N_i, 4) arrays/tensors
        device: tp.Union[torch.device, str] = "cpu",
    ) -> tp.List:
        self.input_proj.to(device)
        self.pos_embed.to(device)
        self.transformer.to(device)
        self.proj_out.to(device)

        batch = []
        for wp in waypoints:
            if not torch.is_tensor(wp):
                wp = torch.tensor(wp, dtype=torch.float32)
            wp = wp.to(device)
            wp = self._resample(wp)      # (n_waypoints, 4)
            wp = self._normalise(wp)     # (n_waypoints, 4)
            batch.append(wp)

        x = torch.stack(batch, dim=0)   # (B, n_waypoints, 4)

        # Project to d_model + add positional embedding
        pos = torch.arange(self.n_waypoints, device=device)
        x = self.input_proj(x) + self.pos_embed(pos).unsqueeze(0)   # (B, N, d_model)

        # Transformer encode
        x = self.transformer(x)          # (B, N, d_model)

        # Project to output_dim
        x = self.proj_out(x)             # (B, N, output_dim)

        mask = torch.ones(x.shape[0], x.shape[1], device=device)    # all valid
        return [x, mask]


class WaypointConditioner(Conditioner):
    """
    Dense per-frame physics conditioner. Replaces the sparse
    cross-attention conditioner with a feature sequence aligned to the
    audio latent time axis, intended to be ADDED element-wise to the
    latent (or projected and added inside the DiT) — O(T_frames) cost
    instead of O(T_latent x T_frames).

    Input:  list (length B) of (N, 4) arrays = [t, az_deg, el_deg, dist_m]
    Output: (B, n_frames, output_dim) tensor + (B, n_frames) mask

    Per-frame raw features (6 dims) before projection:
        t_norm  : t / max_duration                      (in [0, 1])
        nx,ny,nz: unit direction vector from (az, el)
        inv_r2  : 1 / r^2  (clamped, normalised to [0, 1] at dist_clip)
        doppler : log(c / (c - v_r)),  v_r = dr/dt clipped to +-vr_clip*c

    NOTE: integration into the DiT must be wired separately — i.e. the
    model code should consume this conditioner's output via
    `latent = latent + cond` (after a per-channel projection if needed)
    rather than via `cross_attention_cond_ids`.
    """

    def __init__(
        self,
        output_dim: int,
        n_frames: int,
        max_duration: float = 10.0,
        max_dist: float = 50.0,
        dist_clip: float = 0.5,
        sound_speed: float = 343.0,
        vr_clip: float = 0.9,
        hidden_dim: int = 128,
    ):
        super().__init__(output_dim, output_dim, project_out=False)

        self.n_frames = n_frames
        self.max_duration = max_duration
        self.max_dist = max_dist
        self.dist_clip = dist_clip
        self.sound_speed = sound_speed
        self.vr_clip = vr_clip

        self.proj = nn.Sequential(
            nn.Linear(6, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def _interp_to_frames(self, wp: torch.Tensor) -> torch.Tensor:
        """
        wp: (N_orig, 4) = [t, az_deg, el_deg, dist_m]
        Returns: (n_frames, 6) per-frame physics features.
        """
        import numpy as np
        device, dtype = wp.device, wp.dtype

        t_orig    = wp[:, 0].cpu().numpy()
        az_orig   = wp[:, 1].cpu().numpy()
        el_orig   = wp[:, 2].cpu().numpy()
        dist_orig = wp[:, 3].cpu().numpy()

        t_new_np = np.linspace(float(t_orig[0]), float(t_orig[-1]), self.n_frames)
        az   = torch.from_numpy(np.interp(t_new_np, t_orig, az_orig)).to(device, dtype)
        el   = torch.from_numpy(np.interp(t_new_np, t_orig, el_orig)).to(device, dtype)
        dist = torch.from_numpy(np.interp(t_new_np, t_orig, dist_orig)).to(device, dtype)
        t_new = torch.from_numpy(t_new_np).to(device, dtype)

        # az/el (deg) -> unit direction vector
        az_rad = az * (math.pi / 180.0)
        el_rad = el * (math.pi / 180.0)
        nx = torch.cos(el_rad) * torch.cos(az_rad)
        ny = torch.cos(el_rad) * torch.sin(az_rad)
        nz = torch.sin(el_rad)

        # 1/r^2, normalised so dist=dist_clip -> 1.0
        dist_safe = dist.clamp(min=self.dist_clip)
        inv_r2 = (self.dist_clip ** 2) / (dist_safe ** 2)   # in (0, 1]

        # Doppler factor from radial velocity v_r = dr/dt
        dt = (t_new[1] - t_new[0]).clamp(min=1e-3) if self.n_frames > 1 else \
             torch.tensor(1.0, device=device, dtype=dtype)
        v_r = torch.zeros_like(dist)
        if self.n_frames >= 3:
            v_r[1:-1] = (dist[2:] - dist[:-2]) / (2 * dt)
            v_r[0]    = (dist[1] - dist[0]) / dt
            v_r[-1]   = (dist[-1] - dist[-2]) / dt
        elif self.n_frames == 2:
            v = (dist[1] - dist[0]) / dt
            v_r[0] = v; v_r[1] = v

        v_r_norm = (v_r / self.sound_speed).clamp(-self.vr_clip, self.vr_clip)
        doppler  = 1.0 / (1.0 - v_r_norm)
        doppler_log = torch.log(doppler.clamp(min=1e-3))

        t_norm = t_new / self.max_duration

        feats = torch.stack([t_norm, nx, ny, nz, inv_r2, doppler_log], dim=1)
        return feats

    def forward(
        self,
        waypoints: tp.List,
        device: tp.Union[torch.device, str] = "cpu",
    ) -> tp.List:
        self.proj.to(device)

        batch = []
        for wp in waypoints:
            if not torch.is_tensor(wp):
                wp = torch.tensor(wp, dtype=torch.float32)
            wp = wp.to(device)
            batch.append(self._interp_to_frames(wp))

        x = torch.stack(batch, dim=0)         # (B, n_frames, 6)
        x = self.proj(x)                      # (B, n_frames, output_dim)
        # Channel-first for DiT's input_concat_cond path: (B, C, T)
        x = x.transpose(1, 2).contiguous()    # (B, output_dim, n_frames)
        mask = torch.ones(x.shape[0], x.shape[2], device=device)
        return [x, mask]


class WaypointQFormerConditioner(Conditioner):
    """
    Q-Former / Perceiver-style resampler for dense per-frame waypoint physics
    features.

    Input: list (length B) of (n_frames, 6) arrays
        [t_norm, nx, ny, nz, inv_r^2, doppler_log]
        — pre-computed in the dataset directly from the full N-pt waypoint
        trajectory, so no wp10 information bottleneck.

    Pipeline:
        (B, n_frames, 6) -- MLP --> (B, n_frames, d_model)
        Q (n_q learnable queries, d_model) --cross-attn-> (B, n_q, d_model)
        --> output_dim via Linear (if needed)

    Output: (B, n_q, output_dim) tokens + (B, n_q) mask, ready for cross-attn
    consumption by the DiT.
    """

    def __init__(
        self,
        output_dim: int,
        n_frames: int = 160,
        n_queries: int = 16,
        d_model: int = 768,
        n_heads: int = 8,
        hidden_dim: int = 256,
        dropout: float = 0.0,
        in_features: int = 6,
    ):
        super().__init__(d_model, output_dim, project_out=False)

        self.n_frames  = n_frames
        self.n_queries = n_queries
        self.d_model   = d_model

        self.input_proj = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, d_model),
        )

        # learnable queries that summarise the trajectory into n_queries tokens
        self.queries = nn.Parameter(torch.randn(n_queries, d_model) * 0.02)

        # 1-layer cross-attention
        self.attn = nn.MultiheadAttention(
            embed_dim=d_model, num_heads=n_heads,
            dropout=dropout, batch_first=True,
        )
        self.norm_q  = nn.LayerNorm(d_model)
        self.norm_kv = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, hidden_dim * 4),
            nn.GELU(),
            nn.Linear(hidden_dim * 4, d_model),
        )
        self.norm_ffn = nn.LayerNorm(d_model)

    def forward(self, waypoint_features: tp.List[tp.Any], device) -> tp.Any:
        # Stack list of (n_frames, 6) arrays/tensors into (B, n_frames, 6)
        batch = []
        for wf in waypoint_features:
            if not torch.is_tensor(wf):
                wf = torch.as_tensor(np.asarray(wf), dtype=torch.float32)
            wf = wf.to(device=device, dtype=torch.float32)
            if wf.shape[0] != self.n_frames:
                # Light-weight resample along time if a different length is given
                wf_t = wf.transpose(0, 1).unsqueeze(0)  # (1, 6, T)
                wf_t = torch.nn.functional.interpolate(
                    wf_t, size=(self.n_frames,), mode="linear", align_corners=True,
                )
                wf = wf_t.squeeze(0).transpose(0, 1)
            batch.append(wf)
        x = torch.stack(batch, dim=0)                   # (B, n_frames, 6)

        # Project to d_model and cast
        param_dtype = next(self.input_proj.parameters()).dtype
        x = x.to(param_dtype)
        x = self.input_proj(x)                          # (B, n_frames, d_model)

        # Cross-attn from learnable queries to the dense feature sequence
        B = x.shape[0]
        q = self.queries.unsqueeze(0).expand(B, -1, -1) # (B, n_q, d_model)
        q_n  = self.norm_q(q)
        kv_n = self.norm_kv(x)
        attn_out, _ = self.attn(q_n, kv_n, kv_n, need_weights=False)
        h = q + attn_out
        h = h + self.ffn(self.norm_ffn(h))              # (B, n_q, d_model)

        if not isinstance(self.proj_out, nn.Identity):
            proj_out_dtype = next(self.proj_out.parameters()).dtype
            h = h.to(proj_out_dtype)
        h = self.proj_out(h)

        mask = torch.ones(B, self.n_queries, device=device)
        return [h, mask]


class MultiConditioner(nn.Module):
    """
    A module that applies multiple conditioners to an input dictionary based on the keys

    Args:
        conditioners: a dictionary of conditioners with keys corresponding to the keys of the conditioning input dictionary (e.g. "prompt")
        default_keys: a dictionary of default keys to use if the key is not in the input dictionary (e.g. {"prompt_t5": "prompt"})
    """
    def __init__(self, conditioners: tp.Dict[str, Conditioner], default_keys: tp.Dict[str, str] = {}, pre_encoded_keys: tp.List[str] = [], text_mix: tp.Dict[str, tp.Any] = None):
        super().__init__()

        self.conditioners = nn.ModuleDict(conditioners)
        self.default_keys = default_keys
        self.pre_encoded_keys = pre_encoded_keys
        # text_mix: {"id": "<cond_id>", "text_key": "prompt", "prob": 0.1}
        # During training, with given prob, swap the entire batch for this
        # conditioner from its default audio input to the text input, so a
        # CLAP conditioner sees text. Whole-batch swap (not per-sample) so a
        # single forward stays homogeneous.
        self.text_mix = text_mix or {}

    def forward(self, batch_metadata: tp.List[tp.Dict[str, tp.Any]], device: tp.Union[torch.device, str]) -> tp.Dict[str, tp.Any]:
        output = {}

        import random as _random
        for key, conditioner in self.conditioners.items():
            condition_key = key

            # AudioLDM text-mix: swap whole batch to text branch for the
            # configured conditioner with probability `prob` during training.
            if (
                self.training
                and self.text_mix
                and self.text_mix.get("id") == key
                and _random.random() < float(self.text_mix.get("prob", 0.0))
            ):
                condition_key = self.text_mix.get("text_key", "prompt")

            conditioner_inputs = []

            for x in batch_metadata:

                if condition_key not in x:
                    if condition_key in self.default_keys:
                        fb = self.default_keys[condition_key]
                        # Support list of fallback keys. In training, prefer
                        # the first present; in eval, prefer the LAST present
                        # so configs can list ["mono_audio", "prompt_text"]
                        # to mean "audio at train, text at eval".
                        if isinstance(fb, (list, tuple)):
                            present = [k for k in fb if k in x]
                            if not present:
                                raise ValueError(
                                    f"None of fallback keys {fb} found in batch metadata for {condition_key}"
                                )
                            condition_key = present[0] if self.training else present[-1]
                        else:
                            condition_key = fb
                    else:
                        raise ValueError(f"Conditioner key {condition_key} not found in batch metadata")

                #Unwrap the condition info if it's a single-element list or tuple, this is to support collation functions that wrap everything in a list
                if (isinstance(x[condition_key], list) or isinstance(x[condition_key], tuple)) and len(x[condition_key]) == 1:
                    conditioner_input = x[condition_key][0]

                else:
                    conditioner_input = x[condition_key]

                conditioner_inputs.append(conditioner_input)

            if key in self.pre_encoded_keys:
                output[key] = [torch.stack(conditioner_inputs, dim=0).to(device), None]
            else:
                output[key] = conditioner(conditioner_inputs, device)

        return output

def create_multi_conditioner_from_conditioning_config(config: tp.Dict[str, tp.Any], pretransform=None) -> MultiConditioner:
    """
    Create a MultiConditioner from a conditioning config dictionary

    Args:
        config: the conditioning config dictionary
        device: the device to put the conditioners on
    """
    conditioners = {}
    cond_dim = config["cond_dim"]

    default_keys = config.get("default_keys", {})

    pre_encoded_keys = config.get("pre_encoded_keys", [])

    text_mix = config.get("text_mix", None)

    for conditioner_info in config["configs"]:
        id = conditioner_info["id"]

        conditioner_type = conditioner_info["type"]

        conditioner_config = {"output_dim": cond_dim}

        conditioner_config.update(conditioner_info["config"])

        if conditioner_type == "t5":
            conditioners[id] = T5Conditioner(**conditioner_config)
        elif conditioner_type == "clap_text":
            conditioners[id] = CLAPTextConditioner(**conditioner_config)
        elif conditioner_type == "clap_audio":
            conditioners[id] = CLAPAudioConditioner(**conditioner_config)
        elif conditioner_type == "clap":
            conditioners[id] = CLAPConditioner(**conditioner_config)
        elif conditioner_type == "int":
            conditioners[id] = IntConditioner(**conditioner_config)
        elif conditioner_type == "number":
            conditioners[id] = NumberConditioner(**conditioner_config)
        elif conditioner_type == "list":
            conditioners[id] = ListConditioner(**conditioner_config)
        elif conditioner_type == "position":
            conditioners[id] = PositionConditioner(**conditioner_config)
        elif conditioner_type == "waypoint":
            conditioners[id] = WaypointConditioner(**conditioner_config)
        elif conditioner_type == "waypoint_legacy":
            conditioners[id] = WaypointConditionerLegacy(**conditioner_config)
        elif conditioner_type == "waypoint_qformer":
            conditioners[id] = WaypointQFormerConditioner(**conditioner_config)
        elif conditioner_type == "phoneme":
            conditioners[id] = PhonemeConditioner(**conditioner_config)
        elif conditioner_type == "lut":
            conditioners[id] = TokenizerLUTConditioner(**conditioner_config)
        elif conditioner_type == "pretransform":
            sample_rate = conditioner_config.pop("sample_rate", None)
            assert sample_rate is not None, "Sample rate must be specified for pretransform conditioners"

            use_model_pretransform = conditioner_config.pop("use_model_pretransform", False)

            if not use_model_pretransform:
                cond_pretransform = create_pretransform_from_config(conditioner_config.pop("pretransform_config"), sample_rate=sample_rate)
            else:
                assert pretransform is not None, "Model pretransform must be specified for pretransform conditioners"
                cond_pretransform = pretransform

            if conditioner_config.get("pretransform_ckpt_path", None) is not None:
                cond_pretransform.load_state_dict(load_ckpt_state_dict(conditioner_config.pop("pretransform_ckpt_path")))

            conditioners[id] = PretransformConditioner(cond_pretransform, **conditioner_config)
        elif conditioner_type == "source_mix":
            sample_rate = conditioner_config.pop("sample_rate", None)
            assert sample_rate is not None, "Sample rate must be specified for source_mix conditioners"

            use_model_pretransform = conditioner_config.pop("use_model_pretransform", False)

            if not use_model_pretransform:
                cond_pretransform = create_pretransform_from_config(conditioner_config.pop("pretransform_config"), sample_rate=sample_rate)
            else:
                assert pretransform is not None, "Model pretransform must be specified for source_mix conditioners if use_model_pretransform is True"
                cond_pretransform = pretransform

            if conditioner_config.get("pretransform_ckpt_path", None) is not None:
                cond_pretransform.load_state_dict(load_ckpt_state_dict(conditioner_config.pop("pretransform_ckpt_path")))

            conditioners[id] = SourceMixConditioner(cond_pretransform, **conditioner_config)
        else:
            raise ValueError(f"Unknown conditioner type: {conditioner_type}")

    return MultiConditioner(conditioners, default_keys=default_keys, pre_encoded_keys=pre_encoded_keys, text_mix=text_mix)
