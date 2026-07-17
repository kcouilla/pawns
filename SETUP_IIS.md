# Hosting pawns under local IIS

The `webapp/` folder is a self-contained IIS site. All requests (static
files and the `/api/*` JSON endpoints) are routed through the Flask app
(`app.py`) via `wfastcgi` — `app.py` serves `index.html`/`style.css`/
`script.js` itself, since a scoped `path="api/*"` handler mapping doesn't
reliably pass the request path through to Flask's router.

`flask` and `wfastcgi` are already installed (see `requirements.txt`).
Everything below needs an elevated (Run as Administrator) PowerShell
session, since it changes Windows features and IIS's server-wide config.

## 1. Enable the CGI feature

IIS needs the CGI module for FastCGI to work:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CGI -All
```

## 2. Register wfastcgi with IIS

```powershell
wfastcgi-enable
```

This prints a line like:

```
C:\Users\kcoui\AppData\Local\Programs\Python\Python312\python.exe|C:\Users\kcoui\AppData\Local\Programs\Python\Python312\Lib\site-packages\wfastcgi.py
```

`webapp\web.config` already has this exact value filled in as the
`scriptProcessor` (based on this machine's Python install path) — open the
file and confirm the printed line matches what's there. If your Python
install path is different, replace it.

## 3. Unlock the `handlers` section

By default IIS locks `system.webServer/handlers` at the server level, so a
site-level `web.config` isn't allowed to add a handler mapping (our FastCGI
one) until this is unlocked — otherwise every request to the site, even
static files, fails with **HTTP 500.19** ("this configuration section
cannot be used at this path"):

```powershell
& "$env:SystemRoot\System32\inetsrv\appcmd.exe" unlock config /section:system.webServer/handlers
```

## 4. Create the IIS site

Physical path: `C:\Dev\Python\Claude\pawns\webapp`. Suggested port: `8090`
(pick any free port, or a hostname binding if you prefer).

```powershell
Import-Module WebAdministration
New-Website -Name "pawns_web" -PhysicalPath "C:\Dev\Python\Claude\pawns\webapp" -Port 8090
```

If a site already occupies that port, either pick a different `-Port` or
add pawns as an application under an existing site instead:

```powershell
New-WebApplication -Name "pawns_web" -Site "Default Web Site" -PhysicalPath "C:\Dev\Python\Claude\pawns\webapp"
```

(then it'd be reachable at `http://localhost/pawns_web/`)

## 5. Grant the app pool access to Python

`New-Website` creates an app pool running as `ApplicationPoolIdentity` — a
virtual account with no access to your user profile. If Python is a
per-user install (as on this machine, under
`AppData\Local\Programs\Python\...`), that identity can't execute
`python.exe` or read the project files without an explicit grant:

```powershell
icacls "C:\Users\kcoui\AppData\Local\Programs\Python\Python312" /grant "IIS AppPool\<poolname>:(OI)(CI)RX" /T
icacls "C:\Dev\Python\Claude\pawns" /grant "IIS AppPool\<poolname>:(OI)(CI)RX" /T
```

(replace `<poolname>` with your app pool's name — `Get-ChildItem
IIS:\AppPools` lists them; it defaults to the site name, e.g. `pawns_web`,
unless you assigned the site to `DefaultAppPool` or another existing pool)

**Also worth checking**: if `pip install`-ed packages end up split between
`...\Python312\Lib\site-packages` (visible to every account) and
`...\AppData\Roaming\Python\Python312\site-packages` (a *per-user* site,
visible only to your own Windows account, invisible to the app pool
identity), any package that landed in the Roaming location will fail to
import under IIS even though it works fine when you run the app yourself
from a terminal. `python-dateutil` and `six` hit this. If a future
`pip install` adds a new pandas/numpy dependency and IIS starts throwing
`ImportError`s again, check `pip show <package>` for its `Location` and, if
it's under `AppData\Roaming`, fix it with:

```
pip install --force-reinstall --no-deps <package>
```

## 6. Verify

Once the site exists, tell me and I'll check `http://localhost:8090/` and
`http://localhost:8090/api/new-game` respond correctly. If something's
wrong, the FastCGI error log is at `webapp\wfastcgi.log` (path set in
`web.config`).
