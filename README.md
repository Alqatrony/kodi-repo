# Alqatrony Kodi Repository

Kodi repository hosted on GitHub Pages for the `service.subtitles.subdlbridge` addon.

Live URL: `https://alqatrony.github.io/kodi-repo/`

## How to publish an addon update

Follow these steps every time you change the subtitle addon.

### 1. Make your code changes

Edit files inside:

```text
C:\Users\super\OneDrive\Desktop\Alqatrony_Careerfoundry\subdlBridge\service.subtitles.subdlbridge\
```

For example:

- `service.py`
- `warmup.py`
- `resources/` etc.

### 2. Bump the addon version

Open:

```text
C:\Users\super\OneDrive\Desktop\Alqatrony_Careerfoundry\subdlBridge\service.subtitles.subdlbridge\addon.xml
```

Increase the `version` attribute, for example:

```xml
<addon id="service.subtitles.subdlbridge" version="1.2.1" ...>
```

This is what tells Kodi that an update is available.

### 3. Rebuild the Kodi repository

Open a terminal in the **kodi-repo** folder and run the builder:

```powershell
cd C:\Users\super\OneDrive\Desktop\Alqatrony_Careerfoundry\subdlBridge\kodi-repo
python build_repo.py
```

This will:

- Create a versioned zip in `zips/service.subtitles.subdlbridge/`
- Regenerate `zips/addons.xml`
- Regenerate `zips/addons.xml.md5`

### 4. Commit and push

Still in the `kodi-repo` folder:

```powershell
git add .
git commit -m "Bump service.subtitles.subdlbridge to v1.2.1"
git push origin main
```

### 5. Wait for GitHub Pages

After pushing, wait about 30–60 seconds, then verify the live metadata:

```text
https://alqatrony.github.io/kodi-repo/zips/addons.xml
```

You should see the new version there.

### 6. Refresh Kodi

- **If you only changed the subtitle addon:** Kodi will detect the new version automatically. You can also force it with **Add-ons → Check for updates**.
- **If you changed the repository itself** (URL, schema, or repo version), reinstall the repo zip from:
  ```text
  https://alqatrony.github.io/kodi-repo/repository.alqatrony-1.0.1.zip
  ```

## Important notes

- Do **not** change the repository version (`repository.alqatrony/addon.xml`) unless you actually change the repo URL or schema.
- The `index.html` page shows the **repository zip** version, not the subtitle addon version.
- The Kodi repo only tracks the **built** zip files. Keep your own backup of the addon source changes if needed.
