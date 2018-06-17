import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 1.4
import QtGraphicalEffects 1.0

import FireSim 1.0
import "widgets"

Item {
    id: window
    width: 100 //640
    height: 100 //480

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
        onClicked: {
            window.focus = false;
        }
    }

    focus: true
    Keys.enabled: true
    Keys.priority: Keys.BeforeItem
    Keys.forwardTo: canvas

    Shortcut {
        sequence: StandardKey.Open
        onActivated: main.on_btn_open()
    }

    Shortcut {
        sequence: StandardKey.New
        onActivated: main.on_btn_new()
    }

    Shortcut {
        sequence: StandardKey.Save
        onActivated: main.on_btn_save()
    }

    Shortcut {
        sequences: [StandardKey.FullScreen, "F11"]
        onActivated: {
            if (view.visibility == Window.FullScreen)
                view.visibility = Window.Windowed
            else
                view.visibility = Window.FullScreen
        }
    }

    Shortcut {
        sequence: "Ctrl+B"
        onActivated: canvas.model.blurred = !canvas.model.blurred
    }

    Shortcut {
        sequence: "Ctrl+D"
        onActivated: canvas.model.design_mode = true
    }

    Shortcut {
        sequence: "Ctrl+M"
        onActivated: canvas.model.design_mode = false
    }

    Shortcut {
        sequence: "Ctrl+G"
        onActivated: canvas.model.backdrop_enable = !canvas.model.backdrop_enable
    }

    Shortcut {
        sequence: "Ctrl+Q"
        onActivated: main.quit()
    }

    Canvas {
        id: canvas
        anchors {
            left: toolbox.right
            top: parent.top
            bottom: parent.bottom
            right: parent.right
        }
    }

    SystemPalette { id: activePalette }

    Rectangle {
        id: toolbox

        color: "#121212";
        anchors { left: parent.left; top: parent.top; bottom: parent.bottom; }
        width: 48

        Column {
            anchors { horizontalCenter: parent.horizontalCenter; top: parent.top; topMargin: 8; }

            spacing: 8

            ToolButton {
                id: btn_new
                tooltip: "New Scene"
                iconSource: "../res/icon/ic_note_add_white_24dp.png"
                onClicked: main.on_btn_new()
            }

            ToolButton {
                id: btn_load
                tooltip: "Open Scene"
                iconSource: "../res/icon/ic_unarchive_white_24dp.png"
                onClicked: main.on_btn_open()
            }

            ToolButton {
                id: btn_save
                tooltip: "Save Scene"
                iconSource: "../res/icon/ic_save_white_24dp.png"
                onClicked: main.on_btn_save()
            }

            ToolButton {
                id: btn_load_bg
                tooltip: "Open Background Image"
                iconSource: "../res/icon/ic_add_a_photo_white_24dp.png"
                onClicked: main.on_btn_open_backdrop()
            }

            ToolButton {
                tooltip: "Show/Hide Background Image"
                iconSource: "../res/icon/ic_image_white_24dp.png"
                onClicked: canvas.model.backdrop_enable = !canvas.model.backdrop_enable
                checkable: true
                checked: canvas.model.backdrop_enable
            }

            ExclusiveGroup { id: designSimGroup }

            ToolButton {
                tooltip: "Design Mode"
                checkable: true
                checked: canvas.model.design_mode
                exclusiveGroup: designSimGroup
                iconSource: "../res/icon/ic_create_white_24dp.png"
                onClicked: canvas.model.design_mode = true
            }

            ToolButton {
                tooltip: "Simulation Mode"
                checkable: true
                checked: !canvas.model.design_mode
                exclusiveGroup: designSimGroup
                iconSource: "../res/icon/ic_visibility_white_24dp.png"
                onClicked: canvas.model.design_mode = false
            }

            ToolButton {
                tooltip: "Create Linear Group"
                iconSource: "../res/icon/ic_dehaze_white_24dp.png"
                visible: canvas.model.design_mode
                onClicked: canvas.controller.add_new_pixel_group("linear")
            }

            /*ToolButton {
                iconSource: "../res/icon/ic_apps_white_24dp.png"
                visible: canvas.model.design_mode
                onClicked: canvas.model.scene.add_new_pixel_group("rectangular")
            }

            ToolButton {
                iconSource: "../res/icon/ic_radio_button_unchecked_white_24dp.png"
                visible: canvas.model.design_mode
                onClicked: canvas.model.scene.add_new_pixel_group("circular")
            }

            ToolButton {
                iconSource: "../res/icon/ic_grain_white_24dp.png"
                visible: canvas.model.design_mode
                onClicked: canvas.model.scene.add_new_pixel_group("arbitrary")
            }*/

            ToolButton {
                tooltip: "Blur On/Off"
                onClicked: canvas.model.blurred = !canvas.model.blurred
                iconSource: (canvas.model.blurred ?
                             "../res/icon/ic_blur_off_white_24dp.png" :
                             "../res/icon/ic_blur_on_white_24dp.png")
            }

            ToolButton {
                tooltip: "Fullscreen"
                iconSource: ((view.visibility == Window.FullScreen) ?
                             "../res/icon/ic_fullscreen_exit_white_24dp.png" :
                             "../res/icon/ic_fullscreen_white_24dp.png")
                onClicked: {
                    if (view.visibility == Window.FullScreen)
                        view.visibility = Window.Windowed
                    else
                        view.visibility = Window.FullScreen
                }
            }
        }
    }

    Rectangle {
        anchors { top: window.top; right: window.right; margins: 10 }

        width: 120
        height: tool_palette.height + 20
        radius: 5
        color: "#aa232323"
        visible: canvas.model.design_mode

        Column {
            id: tool_palette
            spacing: 6
            anchors { left: parent.left; right: parent.right; margins: 10;
                      verticalCenter: parent.verticalCenter }

            Text {
                anchors { bottomMargin: 8; topMargin: 24 }
                font.pixelSize: 12
                font.bold: true
                color: "#dddddd"
                text: "Scene"
            }

            LabeledInput {
                id: input_scene_name
                key: "Name"
                value: scene.name
            }

            Item {
                width: 1
                height: 6
            }

            Text {
                visible: canvas.selection.length > 0
                anchors { bottomMargin: 8; topMargin: 24 }
                font.pixelSize: 12
                font.bold: true
                color: "#dddddd"
                text: (canvas.selection.length == 1 ? "Pixel Group"
                       : canvas.selection.length + " Items Selected")
            }

            LabeledInput {
                visible: canvas.selection.length == 1
                key: "Strand ID"
                value: canvas.selection.length == 1 ? canvas.selection[0].strand : ""
                onChanged: canvas.selection[0].strand = parseInt(value)
            }

            LabeledInput {
                visible: canvas.selection.length == 1
                key: "Offset"
                value: canvas.selection.length == 1 ? canvas.selection[0].offset : ""
                onChanged: canvas.selection[0].offset = parseInt(value)
            }

            LabeledInput {
                visible: canvas.selection.length == 1
                key: "Pixel Count"
                value: canvas.selection.length == 1 ? canvas.selection[0].count : ""
                onChanged: canvas.selection[0].count = parseInt(value)
            }

            ToolButton {
                visible: ((canvas.selection.length == 1) &&
                          (canvas.selection[0].type == "linear"))
                width: tool_palette.width
                text: "Flip Start/End"
                onClicked: canvas.selection[0].flip()
            }

            ToolButton {
                visible: canvas.selection.length > 0
                width: tool_palette.width
                text: (canvas.selection.length == 1 ? "Delete Group"
                                                    : "Delete Groups")
                textColor: "#f99"
                onClicked: canvas.controller.delete_selected_groups()
            }
        }
    }
}
