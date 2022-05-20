#nullable disable
using System.ComponentModel.DataAnnotations;

namespace Chillax.Models;
public class User
{
    [Key] public Guid Id { get; set; }
    public string Name { get; set; }
}

