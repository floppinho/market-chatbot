import threading
import time
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


sessions = {}
timeout = 60  # 



def timeout_message(to):
    time.sleep(timeout)
    if to in sessions and sessions[to]['active']:
        resp = MessagingResponse()
        resp.message(
            "Você parece ocupado no momento, mas pode conversar comigo mais tarde caso deseje continuar a conversa.")
        sessions[to]['response'].append(str(resp))
        sessions[to]['active'] = False



def send_main_menu(resp):
    resp.message("🛒 *Bem-vindo ao Mercado Online!*\n\nComo posso te ajudar hoje? Selecione uma opção:\n\n1️⃣ Ver Produtos\n2️⃣ Formas de Pagamento\n3️⃣ Horário de Entrega\n4️⃣ Dúvidas e Suporte")



def send_support_menu(resp):
    resp.message(" *Dúvidas e Suporte*\n\nPara suporte, você pode entrar em contato conosco pelo telefone 📞 (XX) XXXX-XXXX ou pelo e-mail 📧 suporte@mercado.com, também temos nosso site 🌐 www.mercado.com.\n\nSelecione uma opção abaixo para continuar:\n1️⃣ Horário de Funcionamento\n2️⃣ Localização do Mercado\n3️⃣ Ofertas, Descontos e Cupons\n0️⃣ Voltar ao Menu Principal")



def send_image(resp, image_url, message_text):
    message = resp.message(message_text)
    message.media(image_url)



def send_return_option(resp, delay=6):
    time.sleep(delay)
    resp.message("0- Voltar ao menu principal")



@app.route("/sms", methods=['POST'])
def sms_reply():
    from_number = request.form['From']
    incoming_msg = request.form['Body'].strip().lower()

    if from_number not in sessions:
        sessions[from_number] = {'response': [],
                                 'active': True, 'state': 'main_menu'}
        resp = MessagingResponse()
        send_main_menu(resp)
        sessions[from_number]['response'].append(str(resp))
        threading.Thread(target=timeout_message, args=(from_number,)).start()
        return str(resp)

    sessions[from_number]['active'] = True
    resp = MessagingResponse()
    state = sessions[from_number].get('state', 'main_menu')

    if state == 'main_menu':
        if incoming_msg == '1':
            image_url = "https://i.pinimg.com/736x/2f/f3/7b/2ff37b4bc6b8859852c9627c4625ab02.jpg"
            send_image(
                resp, image_url, "🛒 Aqui estão alguns de nossos produtos em destaque\n\nDigite 0️⃣ para voltar ao menu ou selecione outra opção")

            threading.Thread(target=send_return_option, args=(resp,)).start()

        elif incoming_msg == '2':
            resp.message(
                "💳 Aceitamos cartões de crédito, débito e pagamentos online via Pix.\n\nDigite 0️⃣ para voltar ao menu ou selecione outra opção")
        elif incoming_msg == '3':
            resp.message(
                "🚚 Entregamos todos os dias, das 8h às 22h.\n\nDigite 0️⃣ para voltar ao menu ou selecione outra opção")
        elif incoming_msg == '4':
            send_support_menu(resp)
            sessions[from_number]['state'] = 'support_menu'
        elif incoming_msg == '0':
            send_main_menu(resp)
        else:
            resp.message(
                "Opção inválida. Por favor, selecione uma das opções do menu.")

    elif state == 'support_menu':
        if incoming_msg == '1':
                resp.message("🕒️ Nosso mercado funciona 24 horas por dia, 7 dias por semana, para melhor atendê-lo.\n\nDigite 0️⃣ para voltar ao menu ou selecione outra opção")
        elif incoming_msg == '2':
                resp.message("🏙️ Estamos localizados na Avenida dos Exemplo, nº 1234, Bairro das Oportunidades, Cidade Exemplar. Venha nos visitar!\n\nDigite 0️⃣ para voltar ao menu ou selecione outra opção")
        elif incoming_msg == '3':
                resp.message("Aproveite nossas ofertas e descontos exclusivos!🎁 Use o cupom DESCONTO20 para 20% off em todas as compras acima de R$100. E mais: ganhe frete grátis em pedidos acima de R$150!💰\n\nDigite 0️⃣ para voltar ao menu ou selecione outra opção")
        elif incoming_msg == '0':
            send_main_menu(resp)
            sessions[from_number]['state'] = 'main_menu'  
        elif incoming_msg == '1':
            send_support_menu(resp)
            sessions[from_number]['state'] = 'support_menu'  
        else:
            resp.message("Opção inválida. Por favor, selecione uma das opções do menu de suporte.")

    sessions[from_number]['response'].append(str(resp))
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
