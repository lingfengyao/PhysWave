import numpy as np

def build_features(waypoints, az_start, el_start, az_end, el_end, seconds_total: float, n_frames: int=160, sound_speed: float=343.0, dist_clip: float=0.5, vr_clip: float=0.9, max_duration: float=10.0) -> np.ndarray:
    """Training-compatible time, direction, inverse-square and radial-velocity features."""
    t_new = np.linspace(0.0, max_duration, n_frames)
    if waypoints is not None and len(waypoints) >= 2:
        wp = waypoints.astype(np.float64)
        t_orig = wp[:, 0]
        az_f = np.interp(t_new, t_orig, wp[:, 1], left=wp[0, 1], right=wp[-1, 1])
        el_f = np.interp(t_new, t_orig, wp[:, 2], left=wp[0, 2], right=wp[-1, 2])
        d_f = np.interp(t_new, t_orig, wp[:, 3], left=wp[0, 3], right=wp[-1, 3])
    else:
        progress = np.clip(t_new / max(float(seconds_total), 1e-06), 0.0, 1.0)
        az_f = az_start + (az_end - az_start) * progress
        el_f = el_start + (el_end - el_start) * progress
        d_f = np.ones(n_frames, dtype=np.float64)
    t_norm = (t_new / max_duration).astype(np.float32)
    az_rad = np.deg2rad(az_f)
    el_rad = np.deg2rad(el_f)
    cos_el = np.cos(el_rad)
    nx = (cos_el * np.cos(az_rad)).astype(np.float32)
    ny = (cos_el * np.sin(az_rad)).astype(np.float32)
    nz = np.sin(el_rad).astype(np.float32)
    d_safe = np.maximum(d_f, dist_clip)
    inv_r2 = (dist_clip ** 2 / d_safe ** 2).astype(np.float32)
    if n_frames >= 2:
        dt = max(t_new[1] - t_new[0], 0.001)
        v_r = -np.gradient(d_f, dt)
    else:
        v_r = np.zeros_like(d_f)
    v_r_norm = np.clip(v_r / sound_speed, -vr_clip, vr_clip)
    doppler = 1.0 / (1.0 - v_r_norm)
    doppler_log = np.log(np.maximum(doppler, 0.001)).astype(np.float32)
    valid = t_new <= min(float(seconds_total), float(max_duration)) + 1e-08
    nx[~valid] = 0.0
    ny[~valid] = 0.0
    nz[~valid] = 0.0
    inv_r2[~valid] = 0.0
    doppler_log[~valid] = 0.0
    return np.stack([t_norm, nx, ny, nz, inv_r2, doppler_log], axis=1).astype(np.float32)
