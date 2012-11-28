import netflix
import urwid
import ConfigParser, os
import time

n_results = 10
#Modify the Flix.cfg file to include your Netflix API key and secret values
config=ConfigParser.ConfigParser()
config.read('Flix.cfg')             #loads the config file

api = netflix.NetflixAPI(api_key=config.get('keysecret', 'key'), api_secret=config.get('keysecret','secret'))

#urwid layout
ask = urwid.Edit(( u"Movie Search by Title\n"))
body = [urwid.Text('Results'), urwid.Divider()]
listboxreset = urwid.ListBox(urwid.SimpleFocusListWalker(body))
listbox = urwid.BoxAdapter(listboxreset, n_results)
reply = urwid.Text("")
button = urwid.Button(u'Exit')
div = urwid.Divider()
pile = urwid.Pile([ask, div, listbox, div, reply, div, button])
top = urwid.Filler(pile, valign='top')

#Populates the listbox based on the netflix api autocomplete results
def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    
    for c in choices:
        c= c['title']['short']     ###Bug Here: Crashes when list has single item
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

#Action when a listbox item is selected
def item_chosen(button, choice):    
    reply.set_text((u"You chose %s" % choice))

#Action when the edit box is updated
def on_ask_change(edit, new_edit_text):

    movies = api.get("catalog/titles/autocomplete", {"term":new_edit_text})
    
    #Handles the case where there are no results
    if 'autocomplete_item' in movies['autocomplete']:
        titlebox = menu(u"Results for %s" %new_edit_text, movies['autocomplete']['autocomplete_item'])
        listbox._set_original_widget(titlebox)     #updates the listbox
    else:        
        listbox._set_original_widget(listboxreset) #clears the listbox
 
#Exit program on click 
def on_exit_clicked(button):
    raise urwid.ExitMainLoop()
    
urwid.connect_signal(ask, 'change', on_ask_change)
urwid.connect_signal(button, 'click', exit_program)

urwid.MainLoop(top).run()