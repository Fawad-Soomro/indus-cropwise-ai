# IndusAstra — NASA Space Apps 2026 Submission Copy

Use this as a draft for the official Team Project page. Review every field and replace placeholders with tested public links before submission.

## Project name
Indus CropWise AI

## High-level project summary
Indus CropWise AI is a web-based decision-support prototype created by Team IndusAstra for NASA Space Apps Challenge 2026, Field Shift. It helps farmers and agricultural learners in the Indus region explore crop-rotation options by combining NASA POWER daily climate information with user-entered farm context, a small crop catalogue and farmer-selected priorities. The application presents temperature, precipitation and humidity indicators, then compares candidate crop sequences using transparent, rule-based scores for water fit, climate fit, soil/rotation diversity and farmer priority fit. Each result includes an explanation and warnings when information is missing. The prototype is for exploration and education; it is not a validated agronomic model and does not guarantee yield, profit, soil improvement or water savings.

## Detailed project description
Indus CropWise AI addresses the Field Shift challenge by turning climate data and farm context into an understandable crop-rotation comparison. A user starts with a demonstration point near Hyderabad, Sindh, or enters other coordinates. The application retrieves daily temperature, maximum and minimum temperature, corrected precipitation and relative humidity from the NASA POWER Daily Point API (Agroclimatology community). Users can inspect the data period, units and source status. The user then enters available farm information such as soil type, pH if known, salinity status, drainage and irrigation availability, and selects priorities such as water saving, soil health, income or food security. A six-crop catalogue covers wheat, cotton, rice, maize, chickpea and mung bean. Four predefined example rotations can be compared, and a custom sequence can also be explored. The comparison is based on four transparent components: Water Fit (30%), Climate Fit (25%), Soil/Rotation Diversity (25%) and Farmer Priority Fit (20%). If a component cannot be computed because required information is missing, the app shows a warning and re-normalizes the remaining weights. The user can inspect component explanations and trade-offs rather than receiving an unexplained single recommendation. In the current version, irrigation availability and salinity directly influence scoring; soil texture, pH, drainage and organic matter are collected as context but are not all incorporated into the present scoring formula. Some farmer-priority tags, including income, are illustrative comparisons and are not market prices or validated economic estimates. The application is a rule-based educational prototype, not a trained machine-learning model or a field-validated agronomy system. Results must be checked with local soil tests and qualified agricultural experts before being used for real farming decisions. The aim is to make NASA climate information and rotation trade-offs more accessible and easier to discuss.

## NASA data / resources used
- **NASA POWER Daily Point API** — Agroclimatology (AG) community.
- Parameters used in the code: `T2M` (temperature at 2 m), `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR` (corrected precipitation), and `RH2M` (relative humidity at 2 m).
- Demonstration point: approximately 25.39° N, 68.37° E near Hyderabad, Sindh, Pakistan.
- Bundled NASA POWER response: 366 daily records covering **2025-11-08 through 2026-11-08**. The included project file carries NASA POWER API response metadata. The tested app data loader returned this as **cached NASA POWER data**, not a fresh live request. For the bundled default location/date range, the app serves this recently saved cache while it is within its 24-hour cache window; it does not force a fresh network request for that same cached query. Other uncached locations/date ranges can trigger a live API request. If NASA POWER is unavailable and no cache exists, the app uses clearly labelled synthetic sample data.
- Official documentation: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Parameter dictionary: https://power.larc.nasa.gov/parameters/

## Space Agency Partner and other data/resources
- **Space Agency Partner datasets:** None are currently integrated in this prototype. Do not list another agency's data as used.
- **Agricultural/crop reference material:** FAO Land & Water Crop Information portal (https://www.fao.org/land-water/databases-and-software/crop-information/en/) and FAO AquaCrop/crop-water concepts (https://www.fao.org/aquacrop/en/). The crop catalogue is a small, general reference set; it is not locally validated for a specific field.
- **Offline fallback:** `data/demo_climate.csv` is AI-generated synthetic demonstration data. It is not NASA data and is used only when NASA POWER and cached response data are unavailable. The app labels it as sample data.
- **Tools/libraries:** Python, Streamlit, Pandas, NumPy, Plotly and Requests.

## AI use disclosure
Claude (Anthropic) assisted with code drafting, debugging, documentation and test development. The synthetic offline fallback climate dataset was AI-generated and is explicitly labelled as synthetic. AI did not generate NASA POWER data. The application scoring is deterministic, rule-based logic, not a trained AI/ML model. The team must review code, calculations, crop facts and citations before publication. No AI-generated photos or videos are included in the application package. If AI-generated images/video are added to the submitted demo, follow the guide's visible watermark and disclosure rules.

## Final project link (replace before submit)
- Public app URL: **[PASTE TESTED PUBLIC APP URL]**
- Public source repository: **[PASTE PUBLIC GITHUB REPOSITORY URL]**

At least one link should let judges access the final project without a password, special permission or registration. Do not submit a localhost URL such as `http://localhost:8501` as the final project link.

## Demo link (replace before submit)
- Seven-slide deck or thirty-second video: **[PASTE PUBLICLY ACCESSIBLE DEMO LINK]**
- This team has prepared a seven-slide presentation. The guide's maximum is seven slides including the title slide. Keep the link accessible to judges.

## Before clicking Submit
1. Confirm all team members are on the official IndusAstra team page and registered for the same Hyderabad, Pakistan virtual Local Event.
2. Confirm the selected challenge is Field Shift.
3. Run the app and check that the data badge says Cached NASA POWER or Live NASA Data. If it says Sample Data, disclose that clearly and do not describe those values as NASA observations.
4. Verify the public app and repository links in an incognito/private browser window.
5. Upload/share the seven-slide demo and make sure viewers do not need permission.
6. Review every source and AI disclosure.
7. Submit through the team's Project tab and save the confirmation screenshot.

## Important technical limitation to disclose
The app collects soil texture, pH, drainage and organic matter, but the current scoring formula does not fully use all those fields. Irrigation availability and salinity do influence the current scores. Crop and rotation scores are illustrative exploratory comparisons, not scientifically validated farm prescriptions.
