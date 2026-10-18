
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  }
});

client.on('qr', qr => {
  qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
  console.log('ربات ضدلینک فعال شد.');
});

client.on('message', async (msg) => {
  try {
    if (!msg.from.endsWith('@g.us')) return;

    const chat = await msg.getChat();
    if (!chat.isGroup) return;

    const senderId = msg.author;
    if (!senderId) return;

    // مدیران گروه مستثنا هستند
    const participant = chat.participants.find(
      p => p.id._serialized === senderId
    );

    if (
      participant &&
      (participant.isAdmin || participant.isSuperAdmin)
    ) {
      return;
    }

    const text = msg.body || '';

    const hasLink =
      /https?:\/\/\S+/i.test(text) ||
      /www\.\S+/i.test(text) ||
      /\b(?:chat\.whatsapp\.com|whatsapp\.com\/channel|t\.me|telegram\.me|discord\.gg|instagram\.com|youtube\.com|youtu\.be|facebook\.com|bit\.ly)\b/i.test(text);

    if (!hasLink) return;

    // ابتدا پیام را حذف کن
    await msg.delete(true);

    // سپس فرستنده را از گروه اخراج کن
    await chat.removeParticipants([senderId]);

    console.log('پیام حذف و درخواست اخراج ارسال شد.');
  } catch (error) {
    console.error('خطا در مدیریت لینک:', error.message);
  }
});

client.initialize();
