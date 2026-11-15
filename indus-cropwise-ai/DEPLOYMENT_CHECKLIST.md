# IndusAstra — Final Deployment and Submission Checklist

## A. Verify on Fawad's Windows laptop
1. Extract the source package to a normal folder such as `D:\IndusAstra\indus-cropwise-ai`.
2. Double-click `run.bat`, or use CMD:
   ```bat
   cd /d D:\IndusAstra\indus-cropwise-ai
   run.bat
   ```
3. Open the local app at `http://localhost:8501`.
4. Check all six pages: Home, Farm Profile, NASA Climate, Crop Catalogue, Rotation Explorer, Methodology & Sources.
5. On NASA Climate, verify the badge. The bundled default-date NASA response should show `CACHED NASA DATA` if the cache file is present and current enough. `LIVE NASA DATA` appears only after a fresh successful API request. `SAMPLE DATA (NOT NASA)` means the app is in synthetic fallback mode.
6. Do not claim live data if the badge says Cached or Sample.
7. Capture real app screenshots using Windows + Shift + S; do not use chart preview HTML as if it were a screenshot of the running app.

## B. Publish the source repository
1. Create a new **public** GitHub repository named `indus-cropwise-ai`.
2. Upload the contents of this folder (not the outer parent folder if it creates an extra nesting level).
3. Ensure `.venv`, `venv`, `__pycache__`, `.pyc`, local secrets and logs are excluded.
4. The bundled NASA POWER response is public API data and can be included if desired; otherwise the app will try the live API and then use its clearly labelled sample fallback.
5. Add a short repository description: `NASA POWER-informed crop-rotation exploration prototype for the NASA Space Apps 2026 Field Shift challenge.`
6. Confirm the repository opens in a private/incognito browser window.

## C. Deploy the Streamlit application
1. Sign in to Streamlit Community Cloud with GitHub.
2. Select the public `indus-cropwise-ai` repository, branch `main`, and entrypoint `app.py`.
3. Deploy and wait for the first build.
4. Open the generated public URL in an incognito/private browser window.
5. Test every main page and the NASA data status. If the app fails to deploy, fix the visible build error and redeploy; never paste an untested deployment URL into NASA.

## D. Official NASA Project page
1. Open the IndusAstra team page and its Project tab.
2. Enter the project name, high-level summary and detailed description from `IndusAstra_NASA_Submission_Copy.md`.
3. Enter the NASA data used and partner/other data accurately. The current app does not integrate a Space Agency Partner dataset.
4. Add the tested public app/repository URL as the final project link.
5. Add the publicly accessible seven-slide deck link as the demo link (maximum seven slides including title), or submit a thirty-second video instead.
6. Add AI-use disclosure; synthetic sample data must not be described as NASA data.
7. Verify every link without logging in or requesting permission.
8. Complete all required fields, submit, and save a screenshot of the submitted/confirmation state.

## E. Local Hyderabad event
The Hyderabad virtual-event description supplied by the team states that project submissions close November 15 at 11:59 PM local time. Check the Hyderabad Local Lead's current WhatsApp announcements for any separate local judging form or earlier local deadline. Do not apply another city's separate deadline to Hyderabad without confirmation.

## F. Final integrity checks
- All six members are registered for the same Hyderabad, Pakistan virtual event and visible on the team page.
- The selected challenge is Field Shift.
- All crop facts and sources are reviewed by the agriculture research owner.
- The app is described as a transparent rule-based prototype, not a trained ML model.
- Results are not described as guaranteed yield, profit or water savings.
- Screenshots and demo show the actual current app.
- Project submission is saved before the official deadline.
