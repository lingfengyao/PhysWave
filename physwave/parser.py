import json
import math
import os
import re

import numpy as np
import requests


SYSTEM_PROMPT = '''Convert one spatial sound instruction into JSON with one event.
Separate a concise English acoustic caption from spatial motion. Preserve the
sound identity. Do not put location, direction, distance or timing in the caption.
For example, "a helicopter circles overhead" has caption "Helicopter rotor noise",
not "a helicopter circles". "A car approaches" has caption "Car engine noise".
Keep trajectory verbs (circles, approaches, recedes, moves) out of the caption.
Coordinates: 0 degrees=front, -90=left, +90=right, +/-180=back;
elevation positive=above, negative=below. Distance is metres; time is seconds.
Use this schema:
{"duration":10,"events":[{"text":"acoustic caption","t_start":0,"t_end":10,
"trajectory":{"type":"static|linear|arc|approach|recede",
"start":{"az":0,"el":0,"r":8},"end":{"az":0,"el":0,"r":8},
"control_points":[],"direction":null,"turns":0},"inferred":[]}]}
Use static for fixed sources; linear for motion between positions; approach or
recede for decreasing or increasing distance; arc for circular motion.
For intermediate positions use control_points=[{"time":5,"az":0,"el":0,"r":8}].
For arcs direction is clockwise or counterclockwise; turns is the number of
revolutions (zero means use the endpoints). Clockwise increases azimuth.
Defaults: 10 seconds, front, ear level, distance 8m; close 2m, very close 1m,
far 25m. List inferred fields in inferred. Distance must be >=0.5m.
Only a single source active over the full 0-10s window is supported. If the
instruction requires multiple independent sources or explicit delayed onset or
early offset, return {"error":"unsupported source count or timing"}.
Return JSON only, without waypoint arrays or Markdown.'''


def _number(value, name):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite number')
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{name} must be a finite number') from None
    if not math.isfinite(value):
        raise ValueError(f'{name} must be finite')
    return value


def to_condition(raw):
    if not isinstance(raw, dict) or 'error' in raw:
        raise ValueError(f'Unsupported instruction: {raw.get("error") if isinstance(raw, dict) else "invalid JSON object"}')
    events = raw.get('events')
    if not isinstance(events, list) or len(events) != 1 or not isinstance(events[0], dict):
        raise ValueError('Expected exactly one sound event')
    event = events[0]
    caption = event.get('text')
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError('Missing acoustic caption')
    if (_number(raw.get('duration', 10), 'duration') != 10 or
        _number(event.get('t_start', 0), 't_start') != 0 or
        _number(event.get('t_end', 10), 't_end') != 10):
        raise ValueError('Only a full 0-10 second event is supported')
    trajectory = event.get('trajectory')
    if not isinstance(trajectory, dict):
        raise ValueError('Missing trajectory')
    kind = trajectory.get('type')
    if kind not in {'static', 'linear', 'arc', 'approach', 'recede'}:
        raise ValueError('Unsupported trajectory type')

    def point(p):
        if not isinstance(p, dict):
            raise ValueError('Each trajectory point must be an object')
        az, el, radius = [_number(p.get(k), k) for k in ('az', 'el', 'r')]
        if abs(el) > 90 or radius < 0.5:
            raise ValueError('Invalid elevation or distance')
        return [az, el, radius]

    start, end = point(trajectory.get('start')), point(trajectory.get('end'))
    controls = trajectory.get('control_points', [])
    if not isinstance(controls, list):
        raise ValueError('control_points must be a list')
    knots = [[0, *start]]
    for control in controls:
        coords = point(control)
        time = _number(control.get('time'), 'control point time')
        if not knots[-1][0] < time < 10:
            raise ValueError('Control point times must strictly increase within (0, 10)')
        knots.append([time, *coords])
    knots.append([10, *end])
    if kind == 'static' and (start != end or controls):
        raise ValueError('Static trajectories must have identical endpoints and no controls')
    if kind == 'approach' and end[2] >= start[2]:
        raise ValueError('Approach distance must decrease')
    if kind == 'recede' and end[2] <= start[2]:
        raise ValueError('Recede distance must increase')
    direction = trajectory.get('direction')
    if direction not in {None, 'clockwise', 'counterclockwise'}:
        raise ValueError('Invalid arc direction')
    turns = _number(trajectory.get('turns', 0), 'turns')
    if turns < 0:
        raise ValueError('turns must be non-negative')
    for i in range(1, len(knots)):
        delta = knots[i][1] - knots[i - 1][1]
        if kind == 'arc' and direction:
            delta = delta % 360 if direction == 'clockwise' else -((-delta) % 360)
        else:
            wrapped = (delta + 180) % 360 - 180
            delta = 180 if wrapped == -180 and delta > 0 else wrapped
        knots[i][1] = knots[i - 1][1] + delta
    if kind == 'arc' and turns:
        if controls or direction is None:
            raise ValueError('Explicit turns require an arc direction and no control points')
        knots[-1][1] = knots[0][1] + (1 if direction == 'clockwise' else -1) * 360 * turns
    knots = np.asarray(knots)
    times = np.linspace(0, 10, 10)
    waypoints = np.column_stack([times, *[np.interp(times, knots[:, 0], knots[:, i]) for i in (1, 2, 3)]])
    return {'caption': caption.strip(), 'waypoints': waypoints.tolist(), 'parsed': raw}


def parse_instruction(instruction, *, model='google/gemini-2.5-flash-lite', provider='openrouter', api_key=None, timeout=60):
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError('instruction must be a non-empty string')
    if not re.fullmatch(r'[A-Za-z0-9._/-]+', model):
        raise ValueError('Invalid model identifier')
    if provider == 'openrouter':
        key = api_key or os.environ.get('OPENROUTER_API_KEY')
        url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {'Authorization': f'Bearer {key}'}
        payload = {'model': model, 'temperature': 0, 'response_format': {'type': 'json_object'},
                   'messages': [{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': instruction}]}
    elif provider == 'google':
        key = api_key or os.environ.get('GEMINI_API_KEY')
        model = model.removeprefix('google/')
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
        headers = {'x-goog-api-key': key}
        payload = {'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]},
                   'contents': [{'role': 'user', 'parts': [{'text': instruction}]}],
                   'generationConfig': {'temperature': 0, 'responseMimeType': 'application/json'}}
    else:
        raise ValueError('provider must be openrouter or google')
    if not key:
        raise ValueError(f'Set {"OPENROUTER_API_KEY" if provider == "openrouter" else "GEMINI_API_KEY"}')
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException:
        raise RuntimeError('Parser request failed; check network connectivity') from None
    if not response.ok:
        raise RuntimeError(f'Parser API returned HTTP {response.status_code}')
    try:
        data = response.json()
        if provider == 'openrouter':
            content = data['choices'][0]['message']['content']
        else:
            content = ''.join(p.get('text', '') for p in data['candidates'][0]['content']['parts'] if not p.get('thought'))
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
        condition = to_condition(json.loads(content))
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        raise ValueError('Parser API did not return a valid trajectory JSON response') from None
    return {**condition, 'instruction': instruction, 'parser': {'provider': provider, 'model': model}}
