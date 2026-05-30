# LTI Setup

Use these steps to install Sidecar as an external app in Canvas.

1. Open the Canvas course or account where Sidecar should be installed.
2. Go to **Settings**.
3. Open the **Apps** tab.
4. Click **View App Configurations**.
5. Click **+ App**.
6. Set **Configuration Type** to **By URL**.
7. Enter the app name, for example:

   ```text
   blog-app
   ```

8. Enter the consumer key:
   Use the deployment's `LTI_KEY` value if it has been changed. 
   Defaults to `lti-key`

9. Enter the shared secret:
   Use the deployment's `LTI_SECRET` value if it has been changed.
   Defaults to `lti-secret`

10. Enter the config URL, with no trailing slash:

   ```text
   https://sidecar.mysidecarhost.com/config_lti
   ```

11. Click **Submit**.

After installation, Sidecar should appear in the Canvas navigation placements. If it does not appear immediately, check **Settings -> Navigation** and enable it where you want it.
