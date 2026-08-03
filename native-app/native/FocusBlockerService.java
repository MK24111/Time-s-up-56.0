package com.timesup.app.focus;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

public class FocusBlockerService extends Service {
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
