package com.bertr.albion;

import org.bukkit.configuration.file.FileConfiguration;

public class ConfigCache {

    public FileConfiguration configuration;

    public ConfigCache(){
        configuration = Albion.getInstance().getConfig();
    }

    public void reloadConfig(){
        Albion.getInstance().reloadConfig();
        configuration = Albion.getInstance().getConfig();
    }
}
