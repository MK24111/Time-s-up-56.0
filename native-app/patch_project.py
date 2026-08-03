"""
Run from the native-app/ folder, AFTER `npx cap add android` has created the
android/ project. Copies the Kotlin plugin files into place and patches
AndroidManifest.xml and MainActivity.java so NativeFocus and its service/
activity are registered. Safe to re-run — it checks before adding anything.
"""
import os
import sys

BASE = "android/app/src/main"
PKG_DIR = "com/timesup/app"
FOCUS_DIR = f"{BASE}/java/{PKG_DIR}/focus"

def copy_plugin_files():
    print(f"Creating directory: {FOCUS_DIR}")
    os.makedirs(FOCUS_DIR, exist_ok=True)
    
    for fname in ["NativeFocusPlugin.kt", "FocusBlockerService.kt", "BlockerOverlayActivity.kt"]:
        src = f"native/{fname}"
        dst = f"{FOCUS_DIR}/{fname}"
        
        if not os.path.exists(src):
            print(f"ERROR: Source file not found: {src}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in native/: {os.listdir('native') if os.path.exists('native') else 'native/ does not exist'}")
            sys.exit(1)
        
        with open(src) as f:
            content = f.read()
        with open(dst, "w") as f:
            f.write(content)
        print(f"Copied {fname} -> {dst}")

def patch_manifest():
    path = f"{BASE}/AndroidManifest.xml"
    if not os.path.exists(path):
        print(f"ERROR: AndroidManifest.xml not found at {path}")
        sys.exit(1)
    
    with open(path) as f:
        manifest = f.read()

    if "xmlns:tools" not in manifest:
        manifest = manifest.replace(
            "<manifest ", '<manifest xmlns:tools="http://schemas.android.com/tools" ', 1
        )

    if "PACKAGE_USAGE_STATS" not in manifest:
        permissions = (
            '\n    <uses-permission android:name="android.permission.PACKAGE_USAGE_STATS" '
            'tools:ignore="ProtectedPermissions" />'
            '\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />'
            '\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />'
            '\n    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />'
            '\n    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />\n'
        )
        manifest = manifest.replace("<application", permissions + "\n    <application", 1)

    if "FocusBlockerService" not in manifest:
        additions = (
            '\n        <service android:name=".focus.FocusBlockerService" '
            'android:foregroundServiceType="specialUse" android:exported="false" />'
            '\n        <activity android:name=".focus.BlockerOverlayActivity" android:exported="false" '
            'android:theme="@style/Theme.AppCompat.NoActionBar" android:excludeFromRecents="true" '
            'android:launchMode="singleTask" />\n    '
        )
        manifest = manifest.replace("</application>", additions + "</application>", 1)

    with open(path, "w") as f:
        f.write(manifest)
    print("Patched AndroidManifest.xml")

def patch_main_activity():
    main_activity_path = None
    java_base = f"{BASE}/java"
    
    print(f"Searching for MainActivity.java in: {java_base}")
    if not os.path.exists(java_base):
        print(f"ERROR: {java_base} does not exist!")
        sys.exit(1)
    
    for root, _dirs, files in os.walk(java_base):
        if "MainActivity.java" in files:
            main_activity_path = os.path.join(root, "MainActivity.java")
            break
    
    if not main_activity_path:
        print("ERROR: MainActivity.java not found!")
        print(f"Contents of {java_base}:")
        for root, dirs, files in os.walk(java_base):
            level = root.replace(java_base, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f'{subindent}{file}')
        sys.exit(1)

    print(f"Found MainActivity.java at: {main_activity_path}")
    with open(main_activity_path) as f:
        content = f.read()

    if "registerPlugin" in content:
        print("MainActivity.java already patched, skipping")
        return

    content = content.replace(
        "import com.getcapacitor.BridgeActivity;",
        "import android.os.Bundle;\nimport com.getcapacitor.BridgeActivity;\nimport com.timesup.app.focus.NativeFocusPlugin;",
    )
    content = content.replace(
        "public class MainActivity extends BridgeActivity {}",
        "public class MainActivity extends BridgeActivity {\n"
        "    @Override\n"
        "    public void onCreate(Bundle savedInstanceState) {\n"
        "        registerPlugin(NativeFocusPlugin.class);\n"
        "        super.onCreate(savedInstanceState);\n"
        "    }\n"
        "}",
    )
    with open(main_activity_path, "w") as f:
        f.write(content)
    print(f"Patched {main_activity_path}")

if __name__ == "__main__":
    try:
        copy_plugin_files()
        patch_manifest()
        patch_main_activity()
        print("Done.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
