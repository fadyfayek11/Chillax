using Chillax.Models;

namespace Chillax.Hubs;
public interface IHubChat
{
    Task Send(DataModel data);
}

