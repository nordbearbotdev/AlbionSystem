package xyz.adhdev.micord.listener;

import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.PlayerDeathEvent;
import xyz.adhdev.micord.DiscordWebhook;
import xyz.adhdev.micord.Main;

import java.io.IOException;

public class PlayerDeathListener implements Listener {
    @EventHandler
    public void OnPlayerDeath(PlayerDeathEvent e) throws IOException {
        if(!Main.plugin.getConfig().getBoolean("Enable Death Message")) return;
        String playerName = e.getEntity().getDisplayName();
        String deathReason = e.getDeathMessage().replace(playerName+" ","");
        String deathMessage = Main.plugin.getConfig().getString("Death Message")
                .replace("{username}", playerName)
                .replace("{reason}", deathReason);
        DiscordWebhook webhook = new DiscordWebhook(Main.plugin.getConfig().getString("Discord Webhook"));
        webhook.setContent(deathMessage);
        webhook.setAvatarUrl(Main.plugin.getConfig().getString("Death Bot Avatar"));
        webhook.setUsername(Main.plugin.getConfig().getString("Death Bot Name"));
        webhook.execute();
    }
}
