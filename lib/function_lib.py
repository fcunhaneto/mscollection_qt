import os
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm.exc import ObjectDeletedError
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QFormLayout, QHBoxLayout, QLineEdit, \
    QComboBox, QPushButton, QSizePolicy, QTableWidget, QFrame, QApplication

import texts

css = 'styles/style.qss'


# Create Frame Layout
def fm_create(parent):
    """
    Create QFormLayout layout.

    :param parent: Widget parent.
    :return: QFormLayout
    """
    fm = QFormLayout(parent)
    fm.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
    fm.setContentsMargins(10, 10, 10, 10)
    fm.setSpacing(10)

    return fm


# Create Line Edit
def le_create(length=32767, tooltip='', place_holder=''):
    """
    Create QLineEdit.

    :param length: Max number of character in QLineEdit.
    :param tooltip: That will fill the QLineEdit tooltip.
    :return: QLineEdit.
    """
    le = QLineEdit()
    le.setMaxLength(length)
    le.setToolTip(tooltip)
    le.setPlaceholderText(place_holder)

    return le


# Create Button
def pb_create(text, font_size=12, height=1024, width=1024 ):
    """
    Create a QPushButton.

    :param text: The text inside the button.
    :param font_size: The font size for text inside the button.
    :param height: The button height.
    :param width: The button width.
    :return: QPushButton.
    """
    pb = QPushButton(text)
    font = QFont()
    font.setPointSize(font_size)
    font.setBold(True)
    font.setWeight(75)
    pb.setFont(font)
    pb.setMaximumHeight(height)
    pb.setMaximumWidth(width)
    size_policy = QSizePolicy(
        QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
    pb.setSizePolicy(size_policy)

    return pb


# Create Combobox
def cb_create(tooltip=''):
    """
    Create QComboBox.

    :param tooltip: string: That will fill the QComboBox tooltip.
    :return: QComboBox
    """
    cb = QComboBox()
    cb.setToolTip(tooltip)
    cb.setEditable(True)
    cb.setInsertPolicy(QComboBox.NoInsert)
    size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    cb.setSizePolicy(size_policy)

    return cb


# Populate CB
def populate_combobox(cb, obj):
    """
    Populated a QComboBox.

    :param cb: The QComboBox that needs to be populated.
    :param obj: List that will populated the QComboBox.
    :param op: That serves as a flag if QComboBox needs to start with a
     blank field.
    """
    cb.clear()
    cb.addItem('', 0)
    for o in obj:
        cb.addItem(o.name, o.id)


# Combobox Info
def get_combobox_info(cb):
    """
    Get the id and name value in selected field in combobox.

    :param cb: QComboBox that the information will be extracted.
    :return: id and name of value in selected field in combobox.
    """
    index = cb.currentIndex()
    name = cb.currentText()
    id = cb.itemData(index)

    return id, name


# Create HBox
def hbox_create(items, spacing=10):
    """
    Create QHBoxLayout.

    :param items: QtWidget: that will be inserted in hbox.
    :param spacing: The space between the widgets.
    :return: QHBoxLayout.
    """
    hbox = QHBoxLayout()
    for item in items:
        hbox.addWidget(item)

    hbox.setSpacing(spacing)

    return hbox


# Create Table
def table_cast_create(headers, tooltip=''):
    """
    Create table with QTableWidget.

    :param headers: List of columns headers title.
    :param tooltip: Text for tooltip.
    :return: Table.
    """
    table = QTableWidget()
    table.setToolTip(tooltip)
    size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    table.setSizePolicy(size_policy)
    table.setFrameShape(QFrame.Panel)
    table.setFrameShadow(QFrame.Plain)
    table.verticalHeader().setVisible(False)
    table.setRowCount(0)
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)

    return table


# Get Line
def line_h_create(height, color):
    """
    Create a horizontal line for insert in layout.

    :param height: String represent the height number and unit ex: '2px'.
    :param color: String with a color for line in hexa format.
    :return: Horizontal line.
    """
    frame = QFrame()
    frame.setStyleSheet(
        "border-width: " + height + "; "
        "border-top-style: none; "
        "border-right-style: none; "
        "border-bottom-style: solid; "
        "border-left-style: none; "
        "border-color: " + color + "; "
    )
    line = frame
    sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(line.sizePolicy().hasHeightForWidth())
    line.setSizePolicy(sizePolicy)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)

    return line

def line_v_create(height, color):
    """
    Create a vertical line for insert in layout.

    :param height: String represent the height number and unit ex: '2px'.
    :param color: String with a color for line in hexa format.
    :return: Vertical line.
    """
    frame = QFrame()
    frame.setStyleSheet(
        "border-width: " + height + "; "
        "border-top-style: none; "
        "border-right-style: none; "
        "border-bottom-style: none; "
        "border-left-style: solid; "
        "border-color: " + color + "; "
    )
    line = frame
    sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setWidthForHeight(line.sizePolicy().hasWidthForHeight())
    line.setSizePolicy(sizePolicy)
    line.setFrameShape(QFrame.VLine)
    line.setFrameShadow(QFrame.Sunken)

    return line

# Messages Box
def show_msg(title, text, icon, button, detail='', info='', ):
    """
    Make a Messagebox.

    :param title: String for the custom title of dialog.
    :param text: String text of the main message to be displayed.
    :param icon: QMessageBox predefined icon corresponding to severity of the
    message.
    :param button: QMessageBox standard buttons.
    :param detail: Dialog shows a Details button. This text appears on clicking
    it.
    :param info: String additional information.
    """
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setText(text)
    msg.setInformativeText(info)
    msg.setWindowTitle(title)
    msg.setDetailedText(detail)
    msg.setStandardButtons(button)
    msg.exec_()


def delete_orphans(session, ch_del, obj, name):
    """
    To delete orphans in database.

    :param session: Sqlalchemy orm session.
    :param ch_del: QCheckBox.
    :param obj: Class from db/db_model.py.
    :param name: Name of class from db/db_model.py.
    """
    for ch in ch_del:
        print(ch.text())
        if ch.isChecked():
            try:
                session.query(obj). \
                    filter(obj.id == ch.text()).delete()
                session.commit()
            except (IntegrityError, ObjectDeletedError) as error:
                session.rollback()
                arg = name + ' ' + ch.text()
                text = texts.msg_delete_erro(arg)
                show_msg(
                    texts.delete_orphans,
                    text,
                    QMessageBox.Critical,
                    QMessageBox.Close,
                    str(error)
                )
                session.commit()


# DB Insert Others
def db_insert_obj(session, obj):
    """
    Insert values in database.

    :param session: Sqlalchemy orm session.
    :param obj: Object who represent table in database.
    :return: Object if it exist or None.
    """
    try:
        session.add(obj)
        session.commit()
        return obj
    except (IntegrityError, DBAPIError) as error:
        session.rollback()
        session.commit()
        text = texts.msg_edit_erro(str(obj))
        show_msg(texts.edit_error, text, QMessageBox.Critical,
                 QMessageBox.Close, str(error))
        return None


# DB Insert Obj
def db_get_id(session, cb, obj):
    """
    Try to insert a object in database if his id not exist.

    :param session: Sqlalchemy orm session.
    :param id: ID to test if it exist.
    :param name: Name to test if it exist.
    :param obj: Object who is insert in database if it's id not exist.
    :return: Object id or None.
    """
    id, name = get_combobox_info(cb)
    obj.name = name
    if id != 0:
        return id
    elif id == 0 and name:
        try:
            session.add(obj)
            session.commit()
            return obj.id
        except (IntegrityError, DBAPIError):
            session.rollback()
            session.commit()
            return None
    else:
        return None


# DB Insert Obj
def db_get_obj(session, id, name, obj):
    """
    Query for object in database if it's id exist else insert the object in
    database.

    :param session: Sqlalchemy orm session.
    :param id: Object id.
    :param name: Attribute name.
    :param obj: Object from db/db_model.py
    :return: Object from database.
    """
    result = None
    if id != 0:
        result = session.query(obj). \
            filter(obj.id == id).first()
    elif id == 0 and name:
        result = db_insert_obj(session, obj(name=name))

    return result


# DB Select All
def db_select_all(session, obj):
    """
    Select all values in database from given object.

    :param session: Sqlalchemy orm session.
    :param obj: Object from db/db_model.py
    :return: All objects with database information.
    """
    return session.query(obj).order_by(obj.name).all()
