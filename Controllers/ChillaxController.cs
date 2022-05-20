using Chillax.Enums;
using Chillax.Hubs;
using Chillax.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;

namespace Chillax.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ChillaxController : ControllerBase
    {
        private IHubContext<ChatHub, IHubChat> _chat;
        private readonly ILogger<ChillaxController> _logger;
        private readonly AppDbContext _context;

        public ChillaxController(ILogger<ChillaxController> logger,AppDbContext context, IHubContext<ChatHub, IHubChat> chat)
        {
            _logger = logger;
            _context = context;
            _chat = chat;
        }
        [HttpPost("User")]
        public async Task<ActionResult> AddUser([FromForm]string userName)
        {
            var isUserNameExist = _context.User.Any(u => u.Name.Equals(userName));
            if (!isUserNameExist)
            {
                var user = new User()
                {
                    Id = Guid.NewGuid(),
                    Name = userName,
                };
                await _context.AddAsync(user);
                await _context.SaveChangesAsync();

                return new OkObjectResult(new AppResponse("Congratulations", ResponseStatus.Success));
            }
            return new BadRequestObjectResult(new AppResponse("Same Name Exist,Please Choose Another One", ResponseStatus.Error));
        }
        
        [HttpPost("Message")]
        public async Task<ActionResult> SendMessage([FromForm]DataModel model)
        {
            var user = _context.User.FirstOrDefault(u => u.Name.Equals(model.UserName));
            if (user is null) return new BadRequestObjectResult(new AppResponse("Server Error", ResponseStatus.Error));
           
            ModelResponse response = new ();
            Result.Fun(model.Message,out response!);
            
            model.Status = GetStatus(response);

            var message = new Messages()
            {
                UserId = user.Id,
                Status = (MessageStatus)model.Status,
                Message = model.Message,
                MessageDate = DateTime.Now
            };
            await _context.Messages.AddAsync(message);
            await _context.SaveChangesAsync();

            await _chat.Clients.All.Send(model);
            _logger.LogInformation("Message has been sent");
            return new OkObjectResult(new DataModel() { Message = message.Message, Status = message.Status, UserName = message.User.Name });
        }

        private static MessageStatus GetStatus(ModelResponse response)
        {
            if (response.IsDepression)
            {
                if (response.IsHateSpeech)
                {
                    return MessageStatus.Depression | MessageStatus.HateSpeech;
                }
                if (response.IsOffensive)
                {
                    return MessageStatus.Depression | MessageStatus.Offensive;
                }

                return MessageStatus.Depression;
            }

            if (response.IsOffensive)
            {
                if (response.IsHateSpeech)
                {
                    return MessageStatus.Offensive | MessageStatus.HateSpeech;
                }

                if (response.IsDepression)
                {
                    return MessageStatus.Offensive | MessageStatus.Depression;
                }
                return MessageStatus.Offensive;
            }

            if (response.IsHateSpeech)
            {
                if (response.IsDepression)
                {
                    return MessageStatus.HateSpeech | MessageStatus.Depression;
                }
                if (response.IsOffensive)
                {
                    return MessageStatus.HateSpeech | MessageStatus.Offensive;
                }
                return MessageStatus.HateSpeech;
            }
            return 0;
        }

        [HttpGet("Messages")]
        public async Task<ActionResult> Messages([FromQuery]int pageIndex = 1, [FromQuery] int pageSize = 10)
        {
            var messages = await _context.Messages.Include(m=>m.User).Select(m=>m).Skip(pageSize * (pageIndex - 1)).Take(pageSize).ToListAsync();
            return new OkObjectResult(messages.Select(m=> new DataModel(){Message = m.Message,Status = m.Status,UserName = m.User.Name}));
        }
    }
}