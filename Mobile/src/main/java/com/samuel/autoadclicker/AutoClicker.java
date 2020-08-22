package com.samuel.autoadclicker;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.Notification;
import android.app.PendingIntent;
import android.content.Intent;
import android.hardware.display.DisplayManager;
import android.media.MediaRecorder;
import android.os.Environment;
import android.os.Parcelable;
import android.os.SystemClock;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.GregorianCalendar;
import java.util.Locale;

public class AutoClicker extends AccessibilityService {
    private String TAG = "Samuel";

    private static String startRecording() {
        Log.i("SamuelNotification", "Starting screenrecording");
        final String fileName = Environment
                .getExternalStoragePublicDirectory(Environment
                        .DIRECTORY_NOTIFICATIONS) + "/" + (new SimpleDateFormat("yyyy-MM-dd'T'HH-mm-ss-SSS", Locale.US)).format(new GregorianCalendar().getTime()) + ".mp4";

        try {
            MainActivity.mMediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
            MainActivity.mMediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
            MainActivity.mMediaRecorder.setOutputFile(fileName);
            MainActivity.mMediaRecorder.setVideoSize(MainActivity.DISPLAY_WIDTH, MainActivity.DISPLAY_HEIGHT);
            MainActivity.mMediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
            MainActivity.mMediaRecorder.setVideoEncodingBitRate(4000000);
            MainActivity.mMediaRecorder.setVideoFrameRate(30);
            MainActivity.mMediaRecorder.prepare();
        } catch (IOException e) {
            e.printStackTrace();
        }

        MainActivity.mVirtualDisplay = MainActivity.mMediaProjection.createVirtualDisplay("Capturing Display",
                MainActivity.DISPLAY_WIDTH, MainActivity.DISPLAY_HEIGHT,
                MainActivity.mScreenDensity,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                MainActivity.mMediaRecorder.getSurface(), null, null);
        sleep(2000);
        MainActivity.mMediaRecorder.start();
        return fileName;
    }

    public static void sleep(long millis) {

        SystemClock.sleep(millis);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        checkNotification(event);

    }

    private void checkNotification(AccessibilityEvent event) {
        if (event.getEventType() == AccessibilityEvent.TYPE_NOTIFICATION_STATE_CHANGED) {
            Parcelable parcelable = event.getParcelableData();
            if (parcelable instanceof Notification) {
                try {
                    Log.i("SamuelNotification", event.getText().toString().replace("\n", "; "));
                    Notification notification = (Notification) parcelable;

                    Intent intent = new Intent(this, MainActivity.class);
                    startActivity(intent);
                    sleep(1000);

                    String fileName = startRecording();

                    sleep(3000);
                    performGlobalAction(AccessibilityService.GLOBAL_ACTION_NOTIFICATIONS);

                    sleep(3000);
                    performGlobalAction(AccessibilityService.GLOBAL_ACTION_BACK);
                    if (notification != null && notification.contentIntent != null) {
                        notification.contentIntent.send();
                        sleep(60000);

                    }

                    stopRecording(fileName);
                    performGlobalAction(AccessibilityService.GLOBAL_ACTION_HOME);

                } catch (PendingIntent.CanceledException e1) {
                    e1.printStackTrace();
                }
            }

        }
    }

    private void stopRecording(String fileName) {
        MainActivity.mMediaRecorder.stop();
        MainActivity.mMediaRecorder.reset();
        MainActivity.mVirtualDisplay.release();

        Log.i("SamuelNotification", "Saving screenrecord at " + fileName);
    }

    @Override
    public void onInterrupt() {
        Log.i(TAG, "onInterrupt");
    }

    @Override
    public void onServiceConnected() {
        Log.i(TAG, "onServiceConnected");
        Intent launchIntent = getPackageManager().getLaunchIntentForPackage(MainActivity.PACKAGE_NAME);
        if (launchIntent != null) {
            startActivity(launchIntent);
        }

        AccessibilityServiceInfo info = getServiceInfo();
        info.eventTypes = AccessibilityEvent.TYPES_ALL_MASK;

        info.packageNames = null;

        info.feedbackType = AccessibilityServiceInfo.FEEDBACK_ALL_MASK;

        info.flags = AccessibilityServiceInfo.DEFAULT |
                AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS |

                AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS |

                AccessibilityServiceInfo.FLAG_REQUEST_ACCESSIBILITY_BUTTON |

                AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS;

        info.notificationTimeout = 100;

        this.setServiceInfo(info);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();

        Log.i(TAG, "Restart service");
        Intent intent = new Intent(this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        Log.i(TAG, "Service restarted");
    }
}