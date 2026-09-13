# SH-304 Mathematical & Scientific Methodology

## 1. Spatial Analysis Grid & CRS Standard

To fuse disparate datasets across resolutions, the system standardizes analysis on a uniform regular grid:
- **Reference CRS:** Geographic `EPSG:4326` (WGS84) for coordinates and GeoJSON export.
- **Metric Calculations:** Project coordinates to local UTM Zone (`EPSG:32643` for Western Ghats, `EPSG:32644` for Uttarakhand) to evaluate physical horizontal distances ($\Delta x, \Delta y$) in true meters.
- **Cell Resolution:** $\Delta \text{deg} = 0.01^\circ$ (approx. $1.08\text{ km} \times 1.11\text{ km}$ at tropical latitudes).

---

## 2. Terrain Metrics Derivation

### 2.1 Slope Gradient (Horn 1981)
Evaluated across a $3 \times 3$ elevation window around cell $z(r, c)$:

$$\begin{bmatrix} z_{1} & z_{2} & z_{3} \\ z_{4} & z_{5} & z_{6} \\ z_{7} & z_{8} & z_{9} \end{bmatrix}$$

Partial derivatives along orthogonal axes:
$$\frac{\partial z}{\partial x} = \frac{(z_{3} + 2z_{6} + z_{9}) - (z_{1} + 2z_{4} + z_{7})}{8 \cdot \Delta x}$$

$$\frac{\partial z}{\partial y} = \frac{(z_{1} + 2z_{2} + z_{3}) - (z_{7} + 2z_{8} + z_{9})}{8 \cdot \Delta y}$$

Terrain slope in degrees:
$$\text{Slope}_{\text{deg}} = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180}{\pi}$$

Slope hazard normalization with saturation at extreme angles ($55^\circ$):
$$S_{\text{slope}} = \min\left(\frac{\text{Slope}_{\text{deg}}}{55.0}, 1.0\right)$$

### 2.2 Hydrological Flow Routing (D8 Algorithm)
Each cell directs runoff to one of its 8 neighboring cells along the direction of steepest downward gradient:
$$\text{gradient}_{k} = \frac{z_{\text{current}} - z_{k}}{\text{distance}_{k}}$$
Upstream contributing area $A(r, c)$ is computed by topological routing in descending elevation order. To normalize the heavy-tailed catchment distribution:
$$S_{\text{flow\_accum}} = \frac{\log_{10}(A) - \log_{10}(A_{\min})}{\log_{10}(A_{\max}) - \log_{10}(A_{\min})}$$

---

## 3. Hydrometeorological Forcing & Antecedent Soil Proxy

### 3.1 IMERG Precipitation Rolling Metrics
From daily precipitation rasters $R(t)$, the following are derived:
- $R_{24h}$: Most recent 24-hour storm total (mm).
- $R_{3d}$: 3-day short-term trigger accumulation $\sum_{t=0}^{2} R(t)$.
- $R_{15d}$: 15-day medium-term antecedent precipitation $\sum_{t=0}^{14} R(t)$.
- Mean intensity: $I = \frac{R_{24h}}{24.0}$ (mm/hr).

### 3.2 Soil-Saturation Proxy (Explicitly Labeled PROXY)
$$\text{AMI} = \frac{0.60 \cdot R_{3d} + 0.40 \cdot R_{15d} \cdot e^{-k \cdot \Delta t}}{S_{\text{max}}}$$
where:
- $k = 0.08\text{ day}^{-1}$ (gravitational soil drainage decay rate)
- $\Delta t = 12\text{ days}$ (effective lag)
- $S_{\text{max}} = 380\text{ mm}$ (soil profile saturation threshold)

Normalized to $[0.0, 1.0]$:
$$S_{\text{soil}} = \text{clip}(\text{AMI}, 0.0, 1.0)$$

---

## 4. Multi-Hazard Risk Scoring

### 4.1 Transparent Weighted Landslide Risk Index
$$\text{Risk}_{\text{landslide}} = w_{\text{rain}} \cdot S_{\text{rain}} + w_{\text{slope}} \cdot S_{\text{slope}} + w_{\text{soil}} \cdot S_{\text{soil}} + w_{\text{hist}} \cdot S_{\text{hist}}$$

**Baseline Versioned Weights (`configs/risk_weights.yaml` v1.0.0):**
- $w_{\text{rain}} = 0.35$ (Dynamic meteorological trigger)
- $w_{\text{slope}} = 0.30$ (Static gravitational potential)
- $w_{\text{soil}} = 0.20$ (Hydrologic pore-pressure proxy)
- $w_{\text{hist}} = 0.15$ (Historical spatial predisposition)
$$\sum w_{i} = 1.00$$

### 4.2 Flash-Flood Topographic Concentration Index
$$\text{Risk}_{\text{flash\_flood}} = 0.50 \cdot S_{R24h} + 0.35 \cdot S_{\text{flow\_accum}} + 0.15 \cdot (1.0 - S_{\text{slope}})$$
*(Valley bottoms with massive upstream drainage receiving torrential rain reach peak flash flood hazard)*.

### 4.3 Classification Tiers
- $[0.00, 0.25) \rightarrow$ **LOW**
- $[0.25, 0.50) \rightarrow$ **MODERATE**
- $[0.50, 0.75) \rightarrow$ **HIGH**
- $[0.75, 1.00] \rightarrow$ **CRITICAL / VERY HIGH**

---

## 5. Lead-Time Estimation (Caine 1980 Reference Model)

Reference global empirical intensity-duration threshold:
$$I_{\text{crit}}(D) = 14.82 \times D^{-0.39}$$
where:
- $I_{\text{crit}}$ is critical mean rainfall intensity (mm/hr)
- $D$ is event duration (hours)

Given current intensity $I_{0}$ and linear rate of rainfall intensification $\alpha = \frac{dI}{dt}$ (mm/hr$^2$):
- If $I_{0} \ge I_{\text{crit}}(D)$: **Threshold Breached** ($T_{\text{lead}} = 0.0\text{ hours}$).
- If $I_{0} < I_{\text{crit}}(D)$ and $\alpha > 0$:
  $$T_{\text{lead}} = \frac{I_{\text{crit}}(D) - I_{0}}{\alpha}$$
  Uncertainty bound: $T_{\text{lead}} \pm 30\%$.
- If $\alpha \le 0$: **Stable Below Threshold** ($T_{\text{lead}} = \text{None}$).

> [!IMPORTANT]
> **Scientific Disclosure:** This represents estimated time to threshold under current rainfall trend using the Caine (1980) global empirical reference curve. It does NOT claim that a landslide will definitely occur at that moment.

---

## 6. Neutral Missing Data Policy

Unrecorded or sparse historical records are never interpreted as zero hazard:
$$\text{Density}_{\text{missing}} = \text{Median}\left(\{\text{Density}_{i} \mid \text{Density}_{i} > 0\}\right)$$
This prevents false-negative under-reporting bias in rural or uninhabited mountainous zones.

---

## 7. Model Validation & Back-Testing Protocol

Historical events from the NASA Global Landslide Catalog (GLC) within the AOI are tested against non-event control samples.

**Mandatory Comparison:**
1. **Rainfall-Only Baseline:** $\text{Risk} = S_{\text{rain}}$
2. **Full Weighted Risk Index:** Data-fusion model

**Performance Metrics Computed:**
- Precision $= \frac{\text{TP}}{\text{TP} + \text{FP}}$
- Recall $= \frac{\text{TP}}{\text{TP} + \text{FN}}$
- False Alarm Rate $(\text{FAR}) = \frac{\text{FP}}{\text{FP} + \text{TN}}$
- Area Under ROC Curve (ROC-AUC)
