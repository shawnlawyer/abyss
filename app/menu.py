from const import *

class Menu():
    def menus_controller(self, thread=None):
        while not thread.stop_event.is_set():

            menus = self.get_menus()
            menu_id, selection = self.draw_menus(menus)
            update_dict = menus[menu_id]['handler'](selection)
            if update_dict is not None:
                self.state.update(update_dict)

    def options_selection_handler(self, key):

        if  self.threads[key].can_start():
            self.threads[key].start()
            if 'callback' in ACTIONS[key]:
                callback = ACTIONS[key]['callback']
                if callback in self.threads:
                    if self.threads[callback].can_start():
                        self.threads[callback].start()


    def draw_menus(self, menus_list, style=BOX_1):
        selections = [0] * len(menus_list)
        console_width = self.term.width

        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)

        active_menu = 0  # keep track of the active menu

        def menu_key_handler(key, selected, options_length):
            nonlocal active_menu
            if key.is_sequence:
                if selected is not None and options_length is not None:
                    if key.name == 'KEY_UP':
                        selected = max(0, selected - 1)
                        return 'field_change_selected', selected
                    elif key.name == 'KEY_DOWN':
                        selected = min(options_length - 1, selected + 1)
                        return 'field_change_selected', selected
                    elif key.name == 'KEY_RIGHT':
                        active_menu = (active_menu + 1) % len(menus_list)  # move to the next menu
                        selections[active_menu] = 0  # select the first option in the new active menu
                        return ('menu_change_selected', selections[active_menu])
                    elif key.name == 'KEY_LEFT':
                        active_menu = (active_menu - 1) % len(menus_list)  # move to the previous menu
                        selections[active_menu] = 0  # select the first option in the new active menu
                        return ('menu_change_selected', selections[active_menu])
                    elif key.name == 'KEY_ENTER':
                        return ('enter', selected)
                elif key.name == 'KEY_ESCAPE':
                    # quit() return to main menu
                    pass
            return ('other', selected)

        custom_handlers = [menu_key_handler]

        while True:
            for menu_id, menu_dict in enumerate(menus_list):
                options = menu_dict['options']
                header = menu_dict.get('header', None)
                x = menu_dict.get('x', 0)
                y = menu_dict.get('y', 1)
                width = menu_dict.get('width', 0)
                height = menu_dict.get('height', len(options))
                selected = selections[menu_id] if menu_id == active_menu else None  # reset selection if not active menu

                lines = []
                for i, option in enumerate(options):
                    line = option + ' *' if i == selected else option
                    #line = option[:width - 4] + '... ' if len(option) > width - 2 else option.ljust(width - 2)
                    #lines.append(self.term.on_black(self.term.white(line)) if i == selected else line)
                    lines.append(line.ljust(width - 2))

                self.draw_box(header, '\n'.join(lines) , width, height, x, y)

                action, selected = self.handle_key_input(selected, len(options), custom_handlers=custom_handlers)
                if action == 'enter':
                    return menu_id, selected
                elif action == 'menu_change_selected':
                    selections[active_menu] = selected
                elif action == 'field_change_selected':
                    selections[menu_id] = selected



if __name__ == "__main__":
    pass