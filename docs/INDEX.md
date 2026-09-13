# TerraSharp Documentation Master Index

Welcome to the complete documentation index for **TerraSharp (SH-304: Hyper-Local Landslide & Flash-Flood Early Warning System)**. This directory contains comprehensive references, scientific derivations, operational playbooks, architecture diagrams, and API specifications.

---

## 🗺️ Recommended Reading Order

```mermaid
flowchart TD
    A["1. README.md<br/>Project Overview & Quickstart"] --> B["2. ARCHITECTURE.md<br/>Pipeline & Component Design"]
    B --> C["3. DATA_SOURCES.md<br/>Sensors, Catalogs & Provenance"]
    C --> D["4. METHODOLOGY.md<br/>Mathematical Equations & Physics"]
    D --> E["5. LIMITATIONS.md<br/>Boundaries & Honesty Disclosures"]
    E --> F["6. DEMO_GUIDE.md<br/>Wayanad & Chamoli Scenarios"]
    F --> G["7. DEPLOYMENT.md<br/>Local, CLI & Docker Setup"]
    G --> H["8. API.md<br/>REST Endpoints & Schemas"]
```

---

## 📚 Complete Document Catalog

| Document | File Path | Focus Area | Target Audience |
|---|---|---|---|
| **System Overview & Quickstart** | [`README.md`](../README.md) | High-level introduction, key features, formulas, benchmark results, and quickstart commands. | All users, developers, evaluators |
| **System Architecture** | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Data-fusion pipeline diagrams, spatial alignment, modules, directory structure, and component data flows. | Architects, backend & data engineers |
| **Data Sources & Provenance** | [`DATA_SOURCES.md`](DATA_SOURCES.md) | Inventory of NASA GPM IMERG, SRTM 30m DEM, NASA GLC, Survey of India, and soil proxy disclosures. | Remote sensing analysts, GIS specialists |
| **Scientific Methodology** | [`METHODOLOGY.md`](METHODOLOGY.md) | Mathematical derivations, Horn (1981) slope, D8 flow routing, Caine (1980) lead-time, weighted scoring index. | Data scientists, hydrologists, geologists |
| **Scientific Limitations** | [`LIMITATIONS.md`](LIMITATIONS.md) | Operational boundaries, proxy disclosures, non-guarantee statements, and false alarm discussions. | Disaster managers, reviewers, evaluators |
| **Interactive Demo Guide** | [`DEMO_GUIDE.md`](DEMO_GUIDE.md) | Step-by-step walkthrough of Wayanad (monsoon deluge) and Chamoli (Himalayan relief) scenarios. | Operators, demonstrators, evaluators |
| **Deployment Guide** | [`DEPLOYMENT.md`](DEPLOYMENT.md) | Local Python/Node setup, Docker containerization, docker-compose, and environment variables. | DevOps, system administrators |
| **REST API Reference** | [`API.md`](API.md) | Full endpoint specifications, parameters, request/response models, and status codes. | Frontend developers, API integrators |
| **Implementation Status** | [`IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md) | 17-phase execution tracking log, files changed, verification tests, and remaining tasks. | Technical project managers, auditors |
| **Original Implementation Plan** | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | Initial architectural design, technical specs, open questions, and approval record. | Technical reviewers |
| **System Walkthrough Artifact** | [`WALKTHROUGH.md`](WALKTHROUGH.md) | Summary of all completed deliverables, test suite logs (19/19 pass), and model benchmarks. | Quality assurance, executive review |

---

## 🔬 Scientific & Provenance Quick Reference

All data layers in TerraSharp strictly declare their physical provenance:

- **`OBSERVED`**: Primary physical measurements (e.g. cadastral boundaries, historical inventory points).
- **`DERIVED`**: Geometrically or mathematically computed from primary data (e.g. Horn 3x3 Slope, D8 Flow Accumulation).
- **`PROXY`**: Indirect empirical indicators (e.g. Antecedent Moisture Index based on 3-day and 15-day rainfall decay; never claimed as direct in-situ sensor data).
- **`MODELLED`**: Weighted hazard index outputs (Landslide Risk, Flash-Flood Concentration).
- **`ESTIMATED`**: Dynamically projected forward in time under current rainfall intensification (Caine 1980 threshold lead time).
- **`DEMO`**: Offline reproducible historical scenarios (Wayanad July 2024 and Chamoli February 2021).
