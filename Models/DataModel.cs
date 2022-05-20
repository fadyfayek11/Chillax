#nullable disable

using Chillax.Enums;
namespace Chillax.Models;
public class DataModel
{
    public string UserName { get; set; }
    public string Message { get; set; }
    public MessageStatus? Status { get; set; }
}

