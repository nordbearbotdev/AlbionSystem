package xyz.adhdev.micord.listener;

import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import xyz.adhdev.micord.DiscordWebhook;
import xyz.adhdev.micord.Main;

import java.io.IOException;

public class PlayerJoinListener implements Listener {
    @EventHandler
    public void OnPlayerJoin(PlayerJoinEvent e) throws IOException {
        if(!Main.plugin.getConfig().getBoolean("Enable Join Message")) return;
        String playerName = e.getPlayer().getDisplayName();
        String joinMessage = Main.plugin.getConfig().getString("Join Message")
                .replace("{username}", playerName);
        DiscordWebhook webhook = new DiscordWebhook(Main.plugin.getConfig().getString("Discord Webhook"));
        webhook.setContent(joinMessage);
        webhook.setAvatarUrl(Main.plugin.getConfig().getString("Join Bot Avatar"));
        webhook.setUsername(Main.plugin.getConfig().getString("Join Bot Name"));
        webhook.execute();
    }
}
