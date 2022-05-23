using Chillax.Enums;
using Chillax.Models;
using Microsoft.AspNetCore.SignalR;

namespace Chillax.Hubs
{
    public class ChatHub : Hub
    {
        public async Task Send(string name, string message,MessageStatus status)
        {
            await Clients.All.SendAsync("Send", name,message,status);

        }
    }
}
