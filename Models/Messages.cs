#nullable disable
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Chillax.Enums;
namespace Chillax.Models;

public class Messages
{
    [Key]
    public int Id { get; set; }
    [ForeignKey("User")]
    public Guid UserId { get; set; }
    public User User { get; set; }
    public string Message { get; set; }
    public MessageStatus Status { get; set; }
    public DateTime MessageDate { get; set; } = DateTime.Now;

}

