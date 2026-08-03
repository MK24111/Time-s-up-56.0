package com.timesup.app.focus

import com.getcapacitor.Plugin
import com.getcapacitor.PluginCall
import com.getcapacitor.PluginMethod
import com.getcapacitor.annotation.CapacitorPlugin

@CapacitorPlugin(name = "NativeFocus")
class NativeFocusPlugin : Plugin() {
    @PluginMethod
    fun echo(call: PluginCall) {
        val value = call.getString("value")
        call.resolve()
    }
}
