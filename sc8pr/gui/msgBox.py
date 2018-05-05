# Copyright 2015-2018 D.G. MacCarthy <https://dmaccarthy.github.io/sc8pr>
#
# This file is part of "sc8pr".
#
# "sc8pr" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "sc8pr" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "sc8pr".  If not, see <http://www.gnu.org/licenses/>.


from sc8pr import Canvas, BOTTOM, TOP
from sc8pr.text import Text, Font, BOLD
from sc8pr.gui.button import Button
from sc8pr.gui.textinput import TextInput


class MessageBox(Canvas):
    "Create simple GUI dialogs"

    def __init__(self, text, userInput=None, buttons=None, title=None, size=(1,1), **kwargs):
        super().__init__(size)
        txtConfig = {"font":Font.sans(), "fontSize":15}
        txtConfig.update(kwargs)
        if buttons is None:
            buttons = ["Okay", "Cancel"]
            if userInput is None: buttons = buttons[:1]
        elif type(buttons) is str: buttons = buttons,
        bSize = None
        icon = True
        for t in buttons:
            t = Text(t).config(**txtConfig)
            if not bSize: bSize = 0, t.height + 12
            self[t.data] = Button(bSize, 2).textIcon(t, icon).config(anchor=BOTTOM) 
            icon = not icon
        self.buttons = self[:len(buttons)]
        for b in self.buttons: b.bind(onaction=self._btnClick)
        self["Text"] = Text(text).config(anchor=TOP, **txtConfig)
        if userInput is not None: self["Input"] = TextInput(userInput,
                "Click to enter your response").config(anchor=TOP,
                bg="white", **txtConfig).bind(onaction=self._tiAction)
        self.arrange().config(bg="#f0f0f0", weight=2, border="blue")
        if title: self.title(title, **txtConfig)

    def arrange(self, padding=12):
        "Adjust size and position of controls"
        try: ti = self["Input"]
        except: ti = None
        btns = self.buttons
        text = self["Text"]
        w = max(b.width for b in btns)
        for b in btns:
            t = b[-1]
            pos = t.pos[0] + (w - b.width) / 2, t.pos[1]
            t.config(pos=pos)
            b._size = w, self[0].height
        w = len(btns) * (w + padding) - padding
        w = max(w, text.width, ti.width if ti else 0) + 2 * padding
        h = btns[0].height + text.height + 3 * padding
        if ti: h += ti.height + padding
        y = max(h, self._size[1])
        self._size = max(w, self._size[0]), y
        x = self.center[0]
        text.config(pos=(x, padding))
        if ti: ti.config(pos=(x, text.height + 2 * padding))
        if len(btns) > 1: x -= (btns[0].width + padding) / 2
        y -= padding
        for b in btns:
            b.config(pos=(x,y))
            x = self._size[0] - x
        return self

    def push(self, img, padding=0):
        "Add content to the top of the dialog, shifting existing content down"
        dh = img.height + padding
        w, h = self._size
        self._size = w, h + dh
        for gr in self:
            x, y = gr.pos
            gr.pos = x, y + dh
        self += img.config(pos=(w/2, padding), anchor=TOP)
        return self

    def title(self, title, padding=4, **kwargs):
        "Add a title bar"
        txtConfig = dict(font=Font.sans(), fontSize=15,
            fontStyle=BOLD, color="white", padding=padding)
        txtConfig.update(kwargs)
        title = Text(title).config(**txtConfig)
        cv = Canvas((self.width, title.height + self.weight), self.border)
        cv += title.config(pos=(cv.center[0], self.weight), anchor=TOP)
        self.push(cv.config(anchor=TOP))
        return self

    def resize(self, size): pass

    def onaction(self, ev):
        "Remove dialog when dismissed"
        self.remove()

    @staticmethod
    def _btnClick(gr, ev):
        "Event handler for button clicks"
        setattr(ev, "action", gr)
        gr.canvas.bubble("onaction", ev)

    @staticmethod
    def _tiAction(gr, ev):
        "Event handler for text input action"
        try:
            if ev.unicode == "\r":
                setattr(ev, "action", gr)
                gr.canvas.bubble("onaction", ev)
        except: pass
