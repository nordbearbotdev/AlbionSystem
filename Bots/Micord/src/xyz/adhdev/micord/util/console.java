package xyz.adhdev.micord.util;

import org.bukkit.Bukkit;

public class console {

    public static void log(String message){
        Bukkit.getConsoleSender().sendMessage(message);
    }
}
