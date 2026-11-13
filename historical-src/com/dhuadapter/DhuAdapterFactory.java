package com.dhuadapter;

import android.app.Activity;
import android.app.AppComponentFactory;
import android.app.Application;
import android.content.pm.ActivityInfo;
import android.content.res.Configuration;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.Log;

/** Public Android APIs only: no native ART hooks, including on translated ARM. */
public final class DhuAdapterFactory extends AppComponentFactory {
    private static final String TAG = "LandscapeCompat";
    private static final int DPI = 240;

    @Override public Application instantiateApplication(ClassLoader cl, String name)
            throws InstantiationException, IllegalAccessException, ClassNotFoundException {
        Application app = super.instantiateApplication(cl, name);
        app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
            @Override public void onActivityPreCreated(Activity activity, Bundle state) {
                activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
                DisplayMetrics dm = activity.getResources().getDisplayMetrics();
                Configuration override = new Configuration();
                override.densityDpi = DPI;
                override.orientation = Configuration.ORIENTATION_LANDSCAPE;
                override.screenWidthDp = Math.round(dm.widthPixels * 160f / DPI);
                override.screenHeightDp = Math.round(dm.heightPixels * 160f / DPI);
                override.smallestScreenWidthDp = Math.min(override.screenWidthDp, override.screenHeightDp);
                try {
                    activity.applyOverrideConfiguration(override);
                } catch (IllegalStateException alreadyRead) {
                    Configuration current = new Configuration(activity.getResources().getConfiguration());
                    current.updateFrom(override);
                    activity.getResources().updateConfiguration(current, dm);
                }
                Log.i(TAG, "Public-API landscape enabled: " + dm.widthPixels + "x" + dm.heightPixels + ", dpi=" + DPI);
            }
            @Override public void onActivityCreated(Activity a, Bundle b) { }
            @Override public void onActivityStarted(Activity a) { }
            @Override public void onActivityResumed(Activity a) {
                if (a.getRequestedOrientation() != ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)
                    a.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
            }
            @Override public void onActivityPaused(Activity a) { }
            @Override public void onActivityStopped(Activity a) { }
            @Override public void onActivitySaveInstanceState(Activity a, Bundle b) { }
            @Override public void onActivityDestroyed(Activity a) { }
        });
        Log.i(TAG, "Compatibility v2 initialized without Pine; root check patched in application DEX");
        return app;
    }
}
