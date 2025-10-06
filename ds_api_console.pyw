from threading import Thread as Td
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox
from openai import OpenAI, OpenAIError
import os

class KeyWin:

    def __init__(self, root:tk.Tk, org):

        self.root = tk.Toplevel(root)
        self.root.transient(root)
        self.root.focus_get()
        self.root.title('Enter Your API Key...')
        self.root.resizable(False, False)
        self.root.geometry()
        self.org = org

        self.frm_burl = tk.Frame(self.root)
        self.burl_label = tk.Label(self.frm_burl, text='Base URL: ')
        self.burl_input = tk.Entry(self.frm_burl)
        self.burl_label.pack(side='left')
        self.burl_input.pack(side='left', fill='x', expand=True)
        self.frm_burl.pack(fill='x', side='top', expand=True, padx=10, pady=10)

        self.frm_api = tk.Frame(self.root)
        self.api_label = tk.Label(self.frm_api, text='API Key: ')
        self.api_input = tk.Entry(self.frm_api, show='#')
        self.api_label.pack(side='left')
        self.api_input.pack(side='left', fill='x', expand=True)
        self.frm_api.pack(fill='x', side='top', expand=True, padx=10, pady=10)

        self.btn = tk.Button(self.root, text='Confirm', command=self.on_btn_pressed)
        self.btn.pack(side='top', fill='x', padx=10, pady=10)
        self.root.protocol('WM_DELETE_WINDOW', None)
        
        self.result = []

    def run(self, base_url_default: str):

        self.burl_input.insert(0, base_url_default)
        self.root.mainloop()

    def on_btn_pressed(self):

        self.result = [self.burl_input.get(), self.api_input.get()]
        self.org.key = self.result[1]
        self.org.base_url = self.result[0]
        self.root.destroy()

class MainWin:

    def __init__(self, font1:str='Calibri', font2:str='Cascadia Code'):

        self.key:str= ''
        self.base_url:str = 'https://api.deepseek.com'
        self.client:OpenAI = None
        self.history:list[dict] = []
        self.history_reasoning:list[str] = []
        self.role_user:str = 'user'
        self.role_ai:str = 'assistant'
        self.role_ai_desc:str = 'You are a helpful assistant.'
        self.temp:float = 1.0
        self.top_p:float = 1.0
        self.freq_penalty:float = 0.0
        self.max_token:int = 128000
        self.model_name = 'deepseek-chat'

        #==== HERE BEGINS GUI LAYOUT ====

        self.root = tk.Tk()
        self.root.title('DeepSeek API Console')
        self.root.geometry('1200x600')
        self.root.config(bg='grey')

        self.font_editor_normal = font.Font(family=font2, size=12)
        self.font_editor_reasoning = font.Font(family=font2, size=12, slant='italic')
        self.font_gui_normal = font.Font(family=font1, size=12)

        self.pw = tk.PanedWindow(orient='vertical')

        self.frm_up = ttk.Frame(self.pw)
        self.dialog = tk.Text(self.frm_up, font=self.font_editor_normal, bg='black', fg='light green')
        self.dialog.pack(fill='both', expand=True)
        self.frm_up.pack(fill='both', expand=True, padx=5, pady=5)
        self.pw.add(self.frm_up)

        self.frm_down = ttk.Frame(self.pw)
        self.entry_input = tk.Text(self.frm_down, font=self.font_editor_normal, bg='light grey')
        self.entry_input.pack(fill='both', expand=True, side='left')
        self.entry_btn = tk.Button(self.frm_down, text='Send', font=self.font_gui_normal, command=self.on_send_message)
        self.entry_btn.pack(fill='both', side='right', ipadx=5)
        self.frm_down.pack(fill='both', expand=True, padx=5, pady=5)
        self.pw.add(self.frm_down)

        self.pw.configure(sashrelief = 'raised', sashpad=5)

        total_width = self.root.winfo_width()
        sash_pos = int(total_width * 0.8)
        self.pw.sash_place(0, sash_pos, 0)

        self.pw.pack(fill='both', expand=True)

        #==== HERE BEGINS TEXT WIDGET FORMATTING INITIATOR ====

        self.dialog.tag_config('reasons', foreground='dark green', font=self.font_editor_reasoning)
        self.dialog.tag_config('info', foreground='dark grey')
        self.dialog.tag_config('error', foreground='orange')

        #==== HERE BEGINS EVENT BINDING ====

        self.entry_input.bind('<Return>', self.on_send_message, add='')
        self.root.protocol('WM_DELETE_WINDOW', self.on_exit_main)

        #==== HERE BEGINS MENU BINDING ====

        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.menu_conn = Menu(self.menu, tearoff=False)
        self.menu_conn.add_command(label='Alter API Key', command=self.input_key)
        self.menu.add_cascade(label='Connection', menu=self.menu_conn, underline=2)

        self.menu_dialog = Menu(self.menu, tearoff=False)
        self.menu_dialog.add_command(label='Clear Dialog History', command=self.clear_history)
        self.menu_dialog.add_radiobutton(label='Use DeepThink (Reasoner)', command=self.change_model_to_reasoner)
        self.menu_dialog.add_radiobutton(label='Use DeepSeek Chat', command=self.change_model_to_chat)
        self.menu.add_cascade(label='Dialog', menu=self.menu_dialog, underline=0)

        self.menu_about = Menu(self.menu, tearoff=False)
        self.menu_about.add_command(label='About', command=self.on_show_about)
        self.menu.add_cascade(label='Misc', menu=self.menu_about, underline=1)

        try:
            script_path = os.path.dirname(__file__)
            f = open(f'{script_path}\\key.asc', 'r')
            self.key = f.readline()
            self.dialog.insert('1.0', 'Standby. API Key loaded.\n\n', 'info')
            f.close()
        except FileNotFoundError as e:
            self.dialog.insert('1.0', f'Standby. No API Key loaded. Reason: No such file (Working at {script_path})\n\n', 'info')

    def on_show_about(self, ev=None):

        messagebox.showinfo(
            title='DeepSeek API Console',
            message='Write purely in Python, with minimal external dependencies (Currently only OpenAI SDK) and love.',
            detail='By Rodent-Nick@Github (nickpang2003@outlook.com)'
        )

    def change_model_to_chat(self, ev=None):
        self.model_name = 'deepseek-chat'

    def change_model_to_reasoner(self, ev=None):
        self.model_name = 'deepseek-reasoner'

    def on_exit_main(self, ev=None):

        res = messagebox.askokcancel(
            title='Confirm Exit?',
            message='Do you want to quit?'
        )

        if res:
            self.root.destroy()

    def clear_history(self):
        
        res = messagebox.askyesno(
            title='Confirm Clear History?',
            message='Do you clear all history? This will also affect LLM\'s performance and cannot be reverted!'
        )

        if not res:
            return

        self.history.clear()
        self.history_reasoning.clear()

        self.dialog.config(state='normal')
        self.dialog.delete('1.0','end')
        self.dialog.insert('1.0', 'Standby.\n\n', 'info')
        self.dialog.config(state='disabled')

    def input_key(self, ev=None):
        
        win = KeyWin(self.root, self)
        win.run(self.base_url)
        if self.client is not None:
            self.client.close()
        self.client = None
        
    def run(self):

        self.root.mainloop()

    def try_establish_client(self, msg:str):

        self.entry_input.config(state='disabled')
        self.entry_btn.config(state='disabled')
        self.update_dialog('[Connecting to %s with key ****%s]\n'%(self.base_url, self.key[-4:]), 'info')

        self.root.title('DeepSeek API Console - Obtaining Client ...')

        self.client = OpenAI(api_key=self.key, base_url=self.base_url)
        self.dialog.config(state='normal')
        self.update_dialog('[Established]\n[Try using this connection to begin chat]\n', 'info')
        self.dialog.config(state='disabled')

        self.require_new_answer(msg)

    def require_new_answer(self, msg:str):

        self.root.title('DeepSeek API Console - Obtaining Answer from Remote Provider ...')

        self.entry_input.config(state='disabled')
        self.entry_btn.config(state='disabled')

        self.update_dialog('[USER]', 'info')
        self.update_dialog('\n%s\n'%(msg,))

        try:
            response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.history + [{'role':self.role_user, 'content':msg}],
                    stream=True
            )

            raw_response = ''
            raw_reasoning = ''
            last_is_reasons = True

            llm_name = ''
            if self.model_name == 'deepseek-chat':
                llm_name = 'DEEPSEEK-CHAT'
            else:
                llm_name = 'DEEPSEEK-REASONER'
            self.update_dialog('[%s]\n'%(llm_name,), 'info')

            for chunk in response:
                if self.model_name == 'deepseek-reasoner' and chunk.choices[0].delta.reasoning_content is not None:
                    reasoning_content = chunk.choices[0].delta.reasoning_content
                    raw_reasoning += reasoning_content
                    self.update_dialog(reasoning_content, 'reasons')
                if chunk.choices[0].delta.content:
                    
                    if last_is_reasons and self.model_name == 'deepseek-reasoner':
                        last_is_reasons = False
                        self.update_dialog('\n\n')
                    
                    content = chunk.choices[0].delta.content
                    raw_response += content
                    self.update_dialog(content)
        
        except OpenAIError as e:
            self.update_dialog(f'<!> ERROR: {e.message}\n\n', 'error')
            self.key = ''
            self.client.close()
            self.client = None

        except e:
            self.update_dialog(f'\n[AN UNKNOWN ERROR HAS OCCURRED.]\n\n', 'error')

            self.entry_input.config(state='normal')
            self.entry_input.delete('1.0', 'end')

            self.history.append({'role':self.role_user, 'content':msg})
            self.history.append({'role':self.role_ai, 'content':raw_response})
            if self.model_name == 'deepseek-reasoner':
                self.history_reasoning.append(raw_reasoning)

        else:
            self.entry_input.config(state='normal')
            self.entry_input.delete('1.0', 'end')

            self.history.append({'role':self.role_user, 'content':msg})
            self.history.append({'role':self.role_ai, 'content':raw_response})
            if self.model_name == 'deepseek-reasoner':
                self.history_reasoning.append(raw_reasoning)
        
        finally:
            self.update_dialog('\n\n*** [END OF RESPONSE] ***\n\n', 'info')
            self.entry_input.config(state='normal')
            self.entry_btn.config(state='normal')
            self.root.title('DeepSeek API Console')

    def on_send_message(self, ev=None):

        # First, check if the input box is empty or not
        u_input = self.entry_input.get('1.0','end').strip().strip('\n')
        if not u_input:
            return
        
        # Then, check if the OpenAI client is generated.
        if self.client is None:
            if self.key == '' or self.base_url == '':
                messagebox.showerror(
                    title='API Information Incomplete',
                    message='Please fill in Base URL and Key before using chat function!'
                )
                win = KeyWin(self.root, self)
                win.run(self.base_url)
                self.on_send_message()
                return
            else:
                Td(target=self.try_establish_client, args=(self.entry_input.get('1.0','end'),)).start()
                return
            
        # Then it should be alright if we just initiate this turn
        Td(target=self.require_new_answer, args=(self.entry_input.get('1.0','end'),)).start()
        return
            
    def update_dialog(self, msg:str, is_reasoning:str=''):
        self.dialog.config(state='normal')
        if is_reasoning == '':
            self.dialog.insert('end', msg)
        else:
            self.dialog.insert('end', msg, is_reasoning)
        self.dialog.see('end')
        self.dialog.config(state='disabled')

if __name__ == '__main__':

    import sys
    if len(sys.argv) >= 3:
        win = MainWin(sys.argv[1], sys.argv[2])
    else:
        win = MainWin()
    win.run()
