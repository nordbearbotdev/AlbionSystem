package xyz.adhdev.micord.listener;

import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerQuitEvent;
import xyz.adhdev.micord.DiscordWebhook;
import xyz.adhdev.micord.Main;

import java.io.IOException;

public class PlayerLeaveListener implements Listener {
    @EventHandler
    public void OnPlayerLeave(PlayerQuitEvent e) throws IOException {
        if(!Main.plugin.getConfig().getBoolean("Enable Leave Message")) return;
        String playerName = e.getPlayer().getDisplayName();
        String leaveMessage = Main.plugin.getConfig().getString("Leave Message")
                .replace("{username}", playerName);
        DiscordWebhook webhook = new DiscordWebhook(Main.plugin.getConfig().getString("Discord Webhook"));
        webhook.setContent(leaveMessage);
        webhook.setAvatarUrl(Main.plugin.getConfig().getString("Leave Bot Avatar"));
        webhook.setUsername(Main.plugin.getConfig().getString("Leave Bot Name"));
        webhook.execute();
    }
}
