using Microsoft.EntityFrameworkCore;

namespace Chillax.Models;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
        
    }
    public DbSet<Messages> Messages { get; set; }
    public DbSet<User> User { get; set; }
}

