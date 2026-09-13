# TerraSharp (SH-304) Mathematical & Scientific Metrics Reference
## Comprehensive Guide to Physical Formats, Geotechnical Equations, Hydrologic Models & Alert Thresholds

---

## 1. Overview of Scientific Metrics

TerraSharp is designed to eliminate black-box opacity in disaster early warning. Every metric calculated across the system is mathematically deterministic, physically grounded, and transparently explained.

### 1.1 Metrics Summary Table

| Metric Symbol | Full Name | Unit | Primary Formula / Algorithm | Normalization Range | Physical Domain |
|---|---|---|---|---|---|
| $\theta$ | **Slope Gradient** | Degrees (°) | Horn (1981) $3 \times 3$ Finite Difference | $[0.0, 55.0^\circ] \rightarrow [0.0, 1.0]$ | Geomorphology / Geotechnical |
| $\psi$ | **Slope Aspect** | Azimuth (°) | $\text{atan2}\left(\frac{\partial z}{\partial y}, -\frac{\partial z}{\partial x}\right)$ | $[0.0^\circ, 360.0^\circ]$ | Topography / Solar exposure |
| $A$ | **Contributing Area** | Cells / $\text{km}^2$ | D8 Steepest Descent Topological Routing | $\log_{10}(A) \rightarrow [0.0, 1.0]$ | Hydrography / Drainage |
| $R_{24\text{h}}$ | **24h Storm Rainfall** | Millimeters (mm) | $\sum_{t=0}^{23} R(t)$ | $[0.0, 250.0\text{ mm}] \rightarrow [0.0, 1.0]$ | Hydrometeorology |
| $R_{3\text{d}}$ | **3-Day Cumulative Rainfall** | Millimeters (mm) | $\sum_{t=0}^{71} R(t)$ | $[0.0, 450.0\text{ mm}] \rightarrow [0.0, 1.0]$ | Hydrometeorology |
| $R_{15\text{d}}$ | **15-Day Cumulative Rainfall** | Millimeters (mm) | $\sum_{t=0}^{359} R(t)$ | $[0.0, 1000.0\text{ mm}] \rightarrow [0.0, 1.0]$ | Hydrometeorology |
| $I_0$ | **Current Rainfall Intensity** | mm / hour | $\frac{R_{24\text{h}}}{24.0}$ | Continuous | Meteorological forcing |
| $\alpha$ | **Intensification Rate** | $\text{mm} / \text{hr}^2$ | $\frac{dI}{dt} \approx \frac{I(t) - I(t-3)}{3.0}$ | Continuous | Dynamic trend |
| $\text{AMI}$ | **Antecedent Moisture Index** | Millimeters (mm) | $\sum_{k=0}^{14} R_k \cdot (0.85)^k$ | $[0.0, 250.0\text{ mm}] \rightarrow [0.0, 1.0]$ | Subsurface pore pressure |
| $S_{\text{hist}}$ | **Historical Susceptibility** | Density $[0, 1]$ | 2D Gaussian Kernel Density (KDE) | AOI Min-Max with Median Baseline | Geological predisposition |
| $\text{Risk}_{\text{landslide}}$ | **Landslide Risk Index** | Dimensionless $[0, 1]$ | Weighted Multi-Factor Formulation | $[0.0, 1.0]$ | Multi-hazard early warning |
| $\text{Risk}_{\text{flash\_flood}}$ | **Flash-Flood Risk Index** | Dimensionless $[0, 1]$ | Orographic Drainage Formulation | $[0.0, 1.0]$ | Surface runoff concentration |
| $I_{\text{crit}}$ | **Caine Critical Intensity** | mm / hour | $14.82 \times D^{-0.39}$ | Continuous | Geotechnical failure boundary |
| $T_{\text{lead}}$ | **Projected Lead Time** | Hours | $\frac{I_{\text{crit}} - I_0}{\alpha}$ | $[0.0, 72.0\text{ hrs}]$ | Early warning lead-time |

---

## 2. Terrain Metrics Derivations

### 2.1 Horn (1981) 3x3 Slope & Aspect Engine

For every cell $z(r, c)$ on a 30m Digital Elevation Model (DEM), an elevation stencil is defined:

$$\mathbf{Z} = \begin{bmatrix} z_1 & z_2 & z_3 \\ z_4 & z_5 & z_6 \\ z_7 & z_8 & z_9 \end{bmatrix} = \begin{bmatrix} z(r-1, c-1) & z(r-1, c) & z(r-1, c+1) \\ z(r, c-1) & z(r, c) & z(r, c+1) \\ z(r+1, c-1) & z(r+1, c) & z(r+1, c+1) \end{bmatrix}$$

Horizontal spatial distances are evaluated in meters:
$$\Delta x = \Delta \text{lon}_{\text{rad}} \times R_{\text{earth}} \times \cos(\text{lat}_{\text{rad}})$$
$$\Delta y = \Delta \text{lat}_{\text{rad}} \times R_{\text{earth}}$$
where $R_{\text{earth}} = 6,371,000\text{ m}$.

#### Orthogonal Partial Derivatives:
$$\frac{\partial z}{\partial x} = \frac{(z_3 + 2z_6 + z_9) - (z_1 + 2z_4 + z_7)}{8 \cdot \Delta x}$$

$$\frac{\partial z}{\partial y} = \frac{(z_1 + 2z_2 + z_3) - (z_7 + 2z_8 + z_9)}{8 \cdot \Delta y}$$

#### Slope Angle in Degrees:
$$\theta = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180^\circ}{\pi}$$

#### Aspect Azimuth in Degrees:
$$\psi = \left(\text{atan2}\left(\frac{\partial z}{\partial y}, -\frac{\partial z}{\partial x}\right) \times \frac{180^\circ}{\pi} + 360^\circ\right) \pmod{360^\circ}$$

#### Geotechnical Normalization ($S_{\text{slope}}$):
$$S_{\text{slope}} = \min\left(1.0, \max\left(0.0, \frac{\theta - 15.0^\circ}{30.0^\circ}\right)\right)$$

- If $\theta < 15^\circ$: $S_{\text{slope}} = 0.0$ (gravitational shear stress is generally insufficient to induce translational failure in typical saprolite / colluvium).
- If $\theta \ge 45^\circ$: $S_{\text{slope}} = 1.0$ (slope reaches maximum geotechnical instability scale).

---

### 2.2 D8 Hydrological Flow Routing & Catchment Accumulation

The **Deterministic Eight-Node (D8)** algorithm routes surface runoff to the steepest downhill neighboring cell:

$$\text{Drop}_{k} = \frac{z_5 - z_k}{d_k}, \quad k \in \{1, \dots, 8\}$$

$$\text{Flow Direction} = \arg\max_{k} (\text{Drop}_k)$$

Contributing upstream catchment area $A(r, c)$ counts the number of cells whose drainage paths pass through cell $(r, c)$. To prevent mega-catchments from dominating the entire distribution:

$$S_{\text{flow\_accum}} = \frac{\log_{10}(A) - \log_{10}(A_{\min})}{\log_{10}(A_{\max}) - \log_{10}(A_{\min})}$$

where $A_{\min} = 1.0$ cell and $A_{\max}$ is the AOI maximum.

---

## 3. Hydrometeorological Metrics & Soil Proxy

### 3.1 IMERG Rolling Accumulations

Given hourly or daily precipitation series $R(t)$ in millimeters:

1. **24-Hour Storm Accumulation ($R_{24\text{h}}$):**
   $$R_{24\text{h}} = \sum_{t=T-23}^{T} R(t)$$
2. **3-Day Short-Term Trigger ($R_{3\text{d}}$):**
   $$R_{3\text{d}} = \sum_{t=T-71}^{T} R(t)$$
3. **15-Day Long-Term Build-up ($R_{15\text{d}}$):**
   $$R_{15\text{d}} = \sum_{t=T-359}^{T} R(t)$$
4. **Current Intensity ($I_0$):**
   $$I_0 = \frac{R_{24\text{h}}}{24.0} \quad (\text{mm/hr})$$
5. **Rainfall Acceleration Trend ($\alpha$):**
   $$\alpha = \frac{dI}{dt} \approx \frac{I(T) - I(T - 48\text{h})}{48.0\text{ hours}} \quad (\text{mm/hr}^2)$$

#### Dynamic Rainfall Score ($S_{\text{rain}}$):
$$R_{24\text{h, norm}} = \text{clip}\left(\frac{R_{24\text{h}}}{250.0}, 0.0, 1.0\right)$$
$$R_{3\text{d, norm}} = \text{clip}\left(\frac{R_{3\text{d}}}{450.0}, 0.0, 1.0\right)$$
$$S_{\text{rain}} = 0.60 \cdot R_{24\text{h, norm}} + 0.40 \cdot R_{3\text{d, norm}}$$

---

### 3.2 Antecedent Moisture Index (AMI) Soil Saturation Proxy

Real-time global in-situ soil moisture sensor grids do not exist. To avoid synthetic guessing, TerraSharp derives an **Antecedent Moisture Index (AMI)** based on exponential gravitational drainage decay:

$$\text{Retention Factor} = 0.85 \quad (15\%\text{ drainage/evapotranspiration loss per day})$$

$$\text{AMI} = \sum_{k=0}^{14} R_k \cdot (0.85)^k = R_0 + 0.85 \cdot R_1 + 0.7225 \cdot R_2 + \dots + (0.85)^{14} \cdot R_{14}$$

where $R_0$ is today's rainfall, $R_1$ is yesterday's, up to $R_{14}$ (14 days prior).

#### Saturation Proxy Normalization ($S_{\text{soil}}$):
$$S_{\text{soil}} = \min\left(1.0, \max\left(0.0, \frac{\text{AMI}}{S_{\text{capacity}}}\right)\right)$$
where default soil profile storage capacity $S_{\text{capacity}} = 250.0\text{ mm}$.

> [!NOTE]
> **Scientific Integrity:** This value is tagged **`PROXY`** across all APIs, database columns, and visual components.

---

## 4. Multi-Factor Hazard Scoring Models

### 4.1 Weighted Landslide Risk Index

$$\text{Risk}_{\text{landslide}} = w_{\text{rain}} \cdot S_{\text{rain}} + w_{\text{slope}} \cdot S_{\text{slope}} + w_{\text{soil}} \cdot S_{\text{soil}} + w_{\text{hist}} \cdot S_{\text{hist}}$$

**Baseline Versioned Weights (`configs/risk_weights.yaml` v1.0.0):**
- $w_{\text{rain}} = 0.35$ (Dynamic triggering rainfall)
- $w_{\text{slope}} = 0.30$ (Static gravitational potential)
- $w_{\text{soil}} = 0.20$ (Antecedent soil pore-pressure proxy)
- $w_{\text{hist}} = 0.15$ (Spatial geological predisposition from NASA GLC)
$$\sum w_i = 0.35 + 0.30 + 0.20 + 0.15 = 1.00$$

### 4.2 Flash-Flood Topographic Concentration Index

$$\text{Risk}_{\text{flash\_flood}} = \min\left(1.0, 0.50 \cdot S_{\text{rain}} + 0.30 \cdot (1.0 - S_{\text{slope}}) + 0.20 \cdot S_{\text{soil}}\right)$$

- $0.50 \cdot S_{\text{rain}}$: Direct surface runoff generation.
- $0.30 \cdot (1.0 - S_{\text{slope}})$: Topographic depressions and flat valleys where flow converges.
- $0.20 \cdot S_{\text{soil}}$: Infiltration capacity reduction (saturated soils force overland flow).

### 4.3 Risk Classification Tiers

| Score Range | Risk Level | Alert State | Operational Meaning | Suggested Response |
|---|---|---|---|---|
| $[0.00, 0.25)$ | **LOW** | `NORMAL` | Normal conditions; minimal failure likelihood | Routine monitoring |
| $[0.25, 0.50)$ | **MODERATE** | `WATCH` | Elevated saturation; active rainfall watch | Issue advisory; inspect drainage |
| $[0.50, 0.75)$ | **HIGH** | `WARNING` | High hazard; slope approaching limit equilibrium | Stage emergency teams; alert shelters |
| $[0.75, 1.00]$ | **VERY HIGH / CRITICAL** | `CRITICAL` | Imminent danger; catastrophic joint concurrence | Simulated immediate evacuation |

---

## 5. Physical False-Alarm Mitigation Gate

To prevent alert fatigue while maintaining 100% sensitivity during real disasters, all evaluations pass through three physical validation gates:

### Gate 1: Flat Terrain Shear Stress Gate ($\theta < 15^\circ$)
In flat or gentle topography ($\theta < 15^\circ$), gravitational shear stress ($\tau = \gamma \cdot h \cdot \sin\theta$) is physically insufficient to overcome internal soil friction ($\phi \approx 25^\circ - 35^\circ$).
$$\text{Factor}_{\text{clamping}} = \left(\frac{\theta}{15.0^\circ}\right)^2 \times 0.20$$
$$\text{Risk}_{\text{final}} = \text{Risk}_{\text{raw}} \times \text{Factor}_{\text{clamping}}$$
*Confidence:* $98.0\%$ | *Reason:* "False Alarm Suppressed: Slope < 15° threshold."

### Gate 2: Unsaturated Matrix Suction Infiltration Buffer
When soils are severely dry ($S_{\text{soil}} < 0.20$) and storm rainfall is moderate ($R_{24\text{h}} < 50\text{ mm}$), subsoil negative pore-water pressure (suction) absorbs rainfall without positive pore-pressure buildup:
$$\text{Risk}_{\text{final}} = \text{Risk}_{\text{raw}} \times 0.50$$
*Confidence:* $92.0\%$ | *Reason:* "Low Risk (Infiltration Buffer): Soil moisture proxy is <20%."

### Gate 3: Catastrophic Joint-Concurrence Confirmation
When steep slopes ($\theta \ge 25^\circ$), saturated soils ($S_{\text{soil}} \ge 0.60$), and critical rainfall ($\frac{I}{I_{\text{crit}}} \ge 0.90$) occur simultaneously:
$$\text{Risk}_{\text{final}} = \min(1.0, \text{Risk}_{\text{raw}} \times 1.15)$$
*Confidence:* $97.5\%$ | *Reason:* "Alert Confirmed: High-hazard joint concurrence of steep slope, saturated soil, and intense rainfall."

---

## 6. Lead-Time Estimation: Caine (1980) Empirical Model

Using the globally recognized **Caine (1980)** empirical threshold:

$$I_{\text{crit}}(D) = 14.82 \times D^{-0.39}$$

where $I_{\text{crit}}$ is critical hourly intensity ($\text{mm/hr}$) and $D$ is event duration in hours.

For standard $D = 24.0\text{ hours}$:
$$I_{\text{crit}}(24) = 14.82 \times 24^{-0.39} \approx 4.29\text{ mm/hr}$$

### Threshold Intensity Ratio:
$$\rho = \frac{I_0}{I_{\text{crit}}}$$

### Lead-Time Calculation ($T_{\text{lead}}$):
1. If $\rho \ge 1.0$:
   $$T_{\text{lead}} = 0.0\text{ hours} \quad \rightarrow \text{Status: \textbf{THRESHOLD\_BREACHED}}$$
2. If $\rho < 1.0$ and $\alpha > 0.05\text{ mm/hr}^2$:
   $$T_{\text{lead}} = \max\left(1.0, \min\left(72.0, \frac{I_{\text{crit}} - I_0}{\alpha}\right)\right) \quad \rightarrow \text{Status: \textbf{IMMINENT\_APPROACHING}}$$
3. If $\alpha \le 0.05\text{ mm/hr}^2$:
   $$T_{\text{lead}} = 48.0\text{ hours} \quad \rightarrow \text{Status: \textbf{SAFE\_MARGIN}}$$

---

## 7. Settlement-Level Spatial Aggregation

To translate raster pixels into actionable governance units, the system intersects the $0.01^\circ$ grid with village cadastral polygons:

$$\text{Village Mean Risk} = \frac{1}{N_{\text{cells}}} \sum_{i=1}^{N_{\text{cells}}} \text{Risk}_i$$
$$\text{Village Peak Risk} = \max_{i} (\text{Risk}_i)$$
$$\text{Critical Area \%} = \frac{\sum_{i} \mathbb{I}(\text{Risk}_i \ge 0.75)}{N_{\text{cells}}} \times 100\%$$
$$\text{Population at Risk} = \text{Population} \times \frac{\text{Critical Area \%}}{100}$$

If $\text{Peak Risk} \ge 0.75$ or $\text{Critical Area \%} \ge 25\%$, the village is escalated to `CRITICAL` alert.
