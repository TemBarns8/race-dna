# Data sources

## Jolpica-F1

Jolpica-F1 provides the driver profile and historical Formula 1
results used during MVP development.

- API: https://api.jolpi.ca/ergast/f1/
- Terms: https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md
- Terms reviewed: 2026-07-04
- MVP usage: non-commercial development

Jolpica data is licensed under CC BY-NC-SA 4.0. Commercial use
requires permission from the service operator.

The Jolpica integration is isolated behind an adapter so that the
source can be replaced without changing Race DNA domain logic.