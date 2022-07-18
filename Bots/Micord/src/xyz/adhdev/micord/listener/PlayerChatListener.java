package xyz.adhdev.micord.listener;

import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import xyz.adhdev.micord.DiscordWebhook;
import xyz.adhdev.micord.Main;

import java.io.IOException;

public class PlayerChatListener implements Listener {
    @EventHandler
    public void OnPlayerChat(AsyncPlayerChatEvent e) throws IOException {
        String message = "";
        if(Main.plugin.getConfig().getBoolean("Block @everyone and @here")){
            message = e.getMessage()
                    .replace("@everyone", "(at)everyone")
                    .replace("@here", "(at)here");
        }else{
            message = e.getMessage();
        }
        String username = e.getPlayer().getDisplayName();
        String avatar = "https://cravatar.eu/helmavatar/"+username+"/190.png";
        DiscordWebhook webhook = new DiscordWebhook(Main.plugin.getConfig().getString("Discord Webhook"));
        webhook.setContent(message);
        webhook.setAvatarUrl(avatar);
        webhook.setUsername(username);
        webhook.execute();
    }
}
