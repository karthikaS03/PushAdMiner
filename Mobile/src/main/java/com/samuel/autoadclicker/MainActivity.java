package com.samuel.autoadclicker;

import android.Manifest;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Point;
import android.hardware.display.VirtualDisplay;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;
import android.provider.Settings;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Display;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityManager;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    public final static int REQUEST_CODE = 12;
    public static final int DISPLAY_WIDTH = 1440;
    public static final int DISPLAY_HEIGHT = 2560;
    private static final boolean DEBUG = false;
    private static final String TAG = "SamuelMainActivity";
    public static String PACKAGE_NAME;
    public static String targetPackageName = "";
    public static Point size = new Point();
    public static VirtualDisplay mVirtualDisplay;
    public static int mScreenDensity;
    public static MediaRecorder mMediaRecorder;
    public static MediaProjection mMediaProjection = null;
    private MediaProjectionManager mProjectionManager;

    public static boolean isAccessibilityEnabled(Context context, String id) {

        List<AccessibilityServiceInfo> runningServices = ((AccessibilityManager) context.getSystemService(Context.ACCESSIBILITY_SERVICE))
                .getEnabledAccessibilityServiceList(AccessibilityEvent.TYPES_ALL_MASK);
        for (AccessibilityServiceInfo service : runningServices) {
            if (id.equals(service.getId())) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        PACKAGE_NAME = this.getPackageName();
    }

    @Override
    protected void onActivityResult(final int requestCode, final int resultCode, final Intent data) {
        if (DEBUG) Log.v(TAG, "onActivityResult:resultCode=" + resultCode + ",data=" + data);
        super.onActivityResult(requestCode, resultCode, data);
        if (321 == requestCode) {
            if (resultCode != Activity.RESULT_OK) {
                return;
            }

            DisplayMetrics metrics = new DisplayMetrics();
            getWindowManager().getDefaultDisplay().getMetrics(metrics);
            mScreenDensity = metrics.densityDpi;
            mMediaRecorder = new MediaRecorder();

            mMediaProjection = mProjectionManager.getMediaProjection(resultCode, data);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();

        checkPermissionReadStorage(this);
        checkPermissionWriteStorage(this);
        openSettingsToGetAccessibilityPermission();

        mProjectionManager = (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        if (mMediaProjection == null) {
            startActivityForResult(mProjectionManager.createScreenCaptureIntent(), 321);
        }
        Display display = getWindowManager().getDefaultDisplay();
        display.getSize(size);
    }

    private String convertStreamToString(InputStream is) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
        StringBuilder sb = new StringBuilder();
        String line = null;
        while ((line = reader.readLine()) != null) {
            sb.append(line).append("\n");
        }
        reader.close();
        return sb.toString();
    }

    public void checkPermissionWriteStorage(Activity activity) {
        if (ContextCompat.checkSelfPermission(activity, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(activity,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE)) {
            } else {
                ActivityCompat.requestPermissions(activity,
                        new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                        REQUEST_CODE + 1);
            }
        }
    }

    public void checkPermissionReadStorage(Activity activity) {
        if (ContextCompat.checkSelfPermission(activity, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(activity,
                    Manifest.permission.READ_EXTERNAL_STORAGE)) {
            } else {
                ActivityCompat.requestPermissions(activity,
                        new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                        REQUEST_CODE);
            }
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
    }

    void openSettingsToGetAccessibilityPermission() {
        if (!isAccessibilityEnabled(this, "com.samuel.autoadclicker/.AutoClicker")) {
            Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
            startActivity(intent);
        }
    }

    public void lanuchApp(String appName) {
        Intent launchIntent = getPackageManager().getLaunchIntentForPackage(appName);
        if (launchIntent != null) {
            targetPackageName = appName;
            startActivity(launchIntent);
        }
    }
}
