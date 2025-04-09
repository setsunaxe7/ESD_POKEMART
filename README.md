# Bulba-Trade
A Pokemon TCG Marketplace web application aiming to provide a pleasant trading and card grading experience for collectors. <br>
Created for IS213 Enterprise Solution Development, a core module for a degree in Information Systems at Singapore Management University.

## Getting Started
### Prerequisites
Docker ([Windows](https://docs.docker.com/desktop/setup/install/windows-install/) | [MacOS](https://docs.docker.com/desktop/setup/install/mac-install/)) <br>
Node Package Manager (npm) ([Link](https://nodejs.org/en/download))

### Setup
Change directory to root folder before coding <br>

#### Frontend:<br>
1) Open a terminal and run the following commands:
```bash
cd nuxt-frontend
npm i
npm run dev
```

#### Backend:<br>
1) Open a terminal and run the following commands:
```bash
cd kong
run.bat
```
⏳ Note: Backend services may take a few moments to fully initialize.

#### Accessing the Web App
Once both the frontend and backend are running, visit:
http://localhost:3000

## Technical Architecture Diagram
<img title="technical overiview diagram" alt="technical overview diagram" src="https://github.com/user-attachments/assets/ad237ffa-832a-4ff0-9b63-efa21e695f64">

## Frameworks & Databases Used
<p align="center"><strong>UI/UX</strong></p>
<div align="center">
	<code><a href="https://ui.nuxt.com/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/nuxt_js.png" alt="Nuxt.js" title="Nuxt.js"/></a></code>
	<code><a href="https://vuejs.org/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/vue_js.png" alt="Vue.js" title="Vue.js"/></a></code>
	<code><a href="https://tailwindcss.com/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/tailwind_css.png" alt="Tailwind CSS" title="Tailwind CSS"/></a></code>
	<code><a href="https://supabase.com/auth"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/supabase.png" alt="Supabase" title="Supabase"/></a></code>
</div>
<p align="center">
<br>
<i> Nuxt.js | Nuxt UI | Vue.js | Tailwind CSS | Supabase Auth</i>
</p>
<br>

<p align="center"><strong>Microservices</strong></p>
<div align="center">
	<code><a href="https://www.python.org/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/python.png" alt="Python" title="Python"/></a></code>
	<code><a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/javascript.png" alt="Javascript" title="Javascript"/></a></code>
	<code><a href="https://flask.palletsprojects.com/en/stable/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/flask.png" alt="Flask" title="Flask"/></a></code>
</div>
<p align="center">
<br>
<i> Python | Javascript | Flask </i>
</p>
<br>

<p align="center"><strong>API Gateway</strong></p>
<div align="center">
	<code><a href="https://konghq.com/"><img width="125" src="https://konghq.com/wp-content/uploads/2018/08/kong-combination-mark-color-256px.png" alt="Kong" title="Kong"/></a></code>
</div>
<p align="center">
<br>
<i> Kong </i>
</p>
<br>

<p align="center"><strong>Inter-Service Communications</strong></p>
<div align="center">
	<code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/rest.png" alt="REST API" title="REST API"/></code>
	<code><a href="https://www.rabbitmq.com/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/rabbitmq.png" alt="RabbitMQ" title="RabbitMQ"/></a></code>
	<code><a href="https://www.rabbitmq.com/docs/stomp"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/websocket.png" alt="Websocket" title="Websocket"/></a></code>
</div>
<p align="center">
<br>
<i> REST API | RabbitMQ | RabbitMQ Web Stomp </i>
</p>
<br>

<p align="center"><strong>Storage Solutions</strong></p>
<div align="center">
	<code><a href="https://supabase.com/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/supabase.png" alt="Supabase" title="Supabase"/></a></code>
	<code><a href="https://www.mongodb.com/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/mongodb.png" alt="MongoDB" title="MongoDB"/></a></code>
	<code><a href="https://redis.io/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/redis.png" alt="Redis Cache" title="Redis Cache"/></a></code>
</div>
<p align="center">
<br>
<i> Supabase | MongoDB | Redis Cache </i>
</p>
<br>

<p align="center"><strong> Other Technologies </strong></p>
<div align="center">
	<code><a href="https://docs.stripe.com/api"><img width="75" src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Stripe_Logo%2C_revised_2016.svg/1280px-Stripe_Logo%2C_revised_2016.svg.png" alt="Stripe API" title="Stripe API"/></a></code>
	<code><a href="https://www.docker.com/"><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/docker.png" alt="Docker" title="Docker"/></a></code>
	<code><a href="https://pokemontcg.io/"><img width="50" src="https://archives.bulbagarden.net/media/upload/thumb/4/47/0094Gengar.png/900px-0094Gengar.png" alt="PokemonTCG API" title="PokemonTCG API"/></a></code>
	<code><a href="https://www.twilio.com/en-us"><img width="100" src="https://upload.wikimedia.org/wikipedia/commons/c/c0/Twilio_logo.png" alt="Twilio" title="Twilio"/></a></code>
</div>
<p align="center">
<br>
<i> Stripe API | Docker | PokemonTCG API | Twilio </i>
</p>
<br>

## Contributors
<b>Team 6</b>
<table border=0>
<tr>
	<td><img src="https://github.com/user-attachments/assets/ac885931-e412-4a19-8e71-35591fe437f7" alt="Ashley" width="110" height="110" style="display:block; margin:0 auto;"></td>
	<td><img src="https://github.com/user-attachments/assets/5685d56c-aaa4-44a9-b6de-ce6509ca2133" alt="Zhao Feng" width="110" height="110" style="display:block; margin:0 auto;"></td>
	<td><img src="https://github.com/user-attachments/assets/4d4ffda2-f1d1-4e59-8555-3349593da847" alt="Elise" width="110" height="110" style="display:block; margin:0 auto;"></td>
	<td><img src="https://github.com/user-attachments/assets/6cef203f-e5ed-44b7-be94-62189880352f" alt="Jagat" width="110" height="110" style="display:block; margin:0 auto;"></td>
	<td><img src="" alt="Yu Feng" width="120" height="120" style="display:block; margin:0 auto;"></td>
	<td><img src="https://github.com/user-attachments/assets/6e5574a7-0e6a-4e5b-849a-6a32a975f260" alt="Jun Yu" width="110" height="110" style="display:block; margin:0 auto;"></td>
</tr>
<tr>
	<th><a href="https://github.com/AshleyCW-pers">Ashley Chiang</a></th>
	<th><a href="https://github.com/angzhaofeng">Ang Zhao Feng</a></th>
	<th><a href="https://github.com/setsunaxe7">Elise Teo</a></th>
	<th><a href="https://github.com/moejag">Jagat Mok</a></th>
	<th><a href="https://github.com/yfbochap">Leong Yu Feng</a></th>
	<th><a href="https://github.com/yapjunyu">Yap Jun Yu</a></th>
</tr>

