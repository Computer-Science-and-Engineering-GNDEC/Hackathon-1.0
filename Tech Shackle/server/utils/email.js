const nodemailer = require("nodemailer");
const pug = require("pug");
const htmlToText = require("html-to-text");
const Event = require("../Models/eventModel");

//new Email(user, url).sendWelcome();
module.exports = class Email {
  constructor(user, url, message) {
    this.to = user.email;
    this.firstName = user.name.split(" ")[0];
    this.url = url;
    this.message = message;
    this.from = `GNDEC <${process.env.EMAIL_FROM}>`;
  }

  newTransport() {
    if (process.env.NODE_ENV === "production") {
      //sendgrid
      return nodemailer.createTransport({
        service: "SendGrid",
        auth: {
          user: process.env.SENDGRID_USERNAME,
          pass: process.env.SENDGRID_PASSWORD,
        },
      });
    }

    return nodemailer.createTransport({
      service: "Gmail",
      host: "smtp.mailtrap.io",
      port: 2525,
      auth: {
        user: "vedicyadav1002@gmail.com",
        pass: "devansh123",
      },
      //Activate in gmail "less secure app" option
    });
  }

  //send the actual email
  async send(template, subject) {
    const events = await (await Event.find()).reverse();
    //Render html based on a pug template
    const html = pug.renderFile(
      `${__dirname}/../views/emails/${template}.pug`,
      {
        firstName: this.firstName,
        url: this.url,
        message: this.message,
        subject,
        events,
      }
    );

    //Define Email options
    const mailOptions = {
      from: this.from,
      to: this.to,
      subject,
      html,
      text: htmlToText.fromString(html),
    };

    //create a transport and send email
    await this.newTransport().sendMail(mailOptions);
  }

  async sendWelcome() {
    await this.send("Welcome", "Welcome to CSI!");
  }

  async sendNotice() {
    await this.send("Event-Notice", "New Event Announcement");
  }

  async sendverificationEmail() {
    await this.send("Verification-mail", "Please verify your email");
  }

  async sendPasswordReset() {
    await this.send(
      "passwordReset",
      "Your password reset token(Valid for 10 minutes)"
    );
  }
};
