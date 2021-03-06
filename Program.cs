using Chillax.Hubs;
using Chillax.Models;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();

//Signalr service
builder.Services.AddCors(option => {
    option.AddPolicy("cors", policy => {
        policy.AllowAnyOrigin().AllowAnyHeader().AllowAnyHeader();
    });
});
builder.Services.AddSignalR();

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection"));
});
var app = builder.Build();

//app.UseEndpoints((c) =>
//{
//    c.MapControllers();

//    c.MapSwagger();
//});

//app.UseSwaggerUI(c =>
//{
//    c.SwaggerEndpoint($"/swagger/Chillax/swagger.json", "API V1");
//});

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
else
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
app.UseDeveloperExceptionPage();
app.UseHttpsRedirection();
app.UseCors("cors");
app.UseAuthorization();

app.MapControllers();
app.MapHub<ChatHub>("/chat");
app.Run();
