package xyz.adhdev.micord;

import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.hooks.AnnotatedEventManager;
import org.bukkit.Bukkit;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.plugin.java.JavaPlugin;
import xyz.adhdev.micord.listener.*;
import xyz.adhdev.micord.util.console;

import javax.security.auth.login.LoginException;
import java.io.File;
import java.io.IOException;

public class Main extends JavaPlugin {
    public static Main plugin;
    @Override
    public void onEnable() {
        updateConfig();
        createConfig();
        if(config.getString("Discord Bot Token").equalsIgnoreCase("NTk1ODMF4kejkyOTkz.1Ns3rT.Y0ur.t0K3n.eMHaM3wYFCf9fE")){
            console.log("§c§lMicord §r> Please Set Your Discord Token");
            Bukkit.getPluginManager().disablePlugin(this);
            return;
        }else if(config.getString("Discord Webhook").equalsIgnoreCase("https://discordapp.com/api/webhooks/insertyourdiscordwebhook")){
            console.log("§c§lMicord §r> Please Set Your Discord Webhook");
            Bukkit.getPluginManager().disablePlugin(this);
            return;
        }
        try
        {
            JDA jda = JDABuilder.createDefault(config.getString("Discord Bot Token"))
                    .setEventManager(new AnnotatedEventManager())
                    .addEventListeners(new UserMessageListener())
                    .build();
            jda.awaitReady();
            console.log("§b§lMicord §r> Success Login");
        }
        catch (LoginException | InterruptedException e)
        {
            e.printStackTrace();
        }
        DiscordWebhook webhook = new DiscordWebhook(config.getString("Discord Webhook"));
        webhook.setContent(config.getString("Micord connected message"));
        try {
            webhook.execute();
        } catch (IOException e) {
            e.printStackTrace();
        }
        plugin = this;
        Bukkit.getServer().getPluginManager().registerEvents(new PlayerChatListener(), this);
        Bukkit.getServer().getPluginManager().registerEvents(new PlayerDeathListener(), this);
        Bukkit.getServer().getPluginManager().registerEvents(new PlayerJoinListener(), this);
        Bukkit.getServer().getPluginManager().registerEvents(new PlayerLeaveListener(), this);
        console.log("§b§lMicord Successfully Enabled");
    }

    @Override
    public void onDisable() {
        DiscordWebhook webhook = new DiscordWebhook(config.getString("Discord Webhook"));
        webhook.setContent(config.getString("Micord disconnected message"));
        try {
            webhook.execute();
        } catch (IOException e) {
            e.printStackTrace();
        }
        console.log("§b§lMicord Disabled");
    }

    public void updateConfig() {
        if(config.getInt("Version") < 3){
            console.log("§b§lMicord §r> Updating Micord");
            config.addDefault("Micord connected message", "Micord Connected");
            config.addDefault("Micord disconnected message", "Micord Disconnected");
            config.set("Version", 3);
            config.options().copyDefaults(true);
            saveConfig();
        }
    }

    public void createConfig() {
        try {
            if(!getDataFolder().exists()) {
                getDataFolder().mkdirs();
            }

            File file = new File(getDataFolder(), "config.yml");
            if (!file.exists()) {
                console.log("Config.yml Not Found, Creating");
                config.addDefault("Channel ID", "653102403725426701");
                config.addDefault("Micord connected message", "Micord Connected");
                config.addDefault("Micord disconnected message", "Micord Disconnected");
                config.addDefault("Block @everyone and @here", false);
                config.addDefault("Discord Bot Token", "NTk1ODMF4kejkyOTkz.1Ns3rT.Y0ur.t0K3n.eMHaM3wYFCf9fE");
                config.addDefault("Discord Webhook", "https://discordapp.com/api/webhooks/insertyourdiscordwebhook");
                config.addDefault("Discord Chat Format", "&b&l[Discord] &r<{userTag}> {userMessage}");
                config.addDefault("Enable Death Message", true);
                config.addDefault("Death Bot Name", "Death Notification");
                config.addDefault("Death Bot Avatar", "https://i.ibb.co/CwvByzp/a-4a2d4c71d0ec0c7f72792d7280a6529d.webp");
                config.addDefault("Death Message", "```{username} {reason}```");
                config.addDefault("Enable Join Message", true);
                config.addDefault("Join Bot Name", "Join Notification");
                config.addDefault("Join Bot Avatar", "https://i.ibb.co/CwvByzp/a-4a2d4c71d0ec0c7f72792d7280a6529d.webp");
                config.addDefault("Join Message", "```{username} joined the game```");
                config.addDefault("Enable Leave Message", true);
                config.addDefault("Leave Bot Name", "Leave Notification");
                config.addDefault("Leave Bot Avatar", "https://i.ibb.co/CwvByzp/a-4a2d4c71d0ec0c7f72792d7280a6529d.webp");
                config.addDefault("Leave Message", "{username} left the game");
                config.addDefault("Version", 3);
                config.options().copyDefaults(true);
                saveConfig();
                this.getConfig();
            } else {
                console.log("Config.yml Found, Loading");
                this.getConfig();
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    FileConfiguration config = getConfig();
}
