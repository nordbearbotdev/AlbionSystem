package xyz.adhdev.micord.listener;

import net.dv8tion.jda.api.events.message.guild.GuildMessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import net.dv8tion.jda.api.hooks.SubscribeEvent;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import xyz.adhdev.micord.Main;

public class UserMessageListener extends ListenerAdapter {

    @SubscribeEvent
    public void onGuildMessage(GuildMessageReceivedEvent e) {
        if(e.getAuthor().isBot() || e.getAuthor().isFake()) return;
        if(e.getChannel() == e.getJDA().getTextChannelById(Main.plugin.getConfig().getString("Channel ID"))){
            String userTag = e.getAuthor().getAsTag();
            String userMessage = e.getMessage().getContentDisplay();
            String discordFormat = Main.plugin.getConfig().getString("Discord Chat Format")
                    .replace("{userTag}", userTag)
                    .replace("{userMessage}", userMessage)
                    .replace("&", "§");
            if(userMessage.isEmpty()) return;
            for(Player player : Bukkit.getOnlinePlayers()){
                player.sendMessage(discordFormat);
            }
        }
    }
}
