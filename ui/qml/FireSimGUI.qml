import QtQuick 2.0
import QtQuick.Window 2.2
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
    Keys.onReleased: {
        if (event.key == Qt.Key_Q && event.modifiers == Qt.ControlModifier) {
            main.quit()
        }
    }
    Keys.forwardTo: canvas

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

        width: 130
        color: "#121212";
        anchors { left: parent.left; top: parent.top; bottom: parent.bottom; }

        Column {
            anchors { horizontalCenter: parent.horizontalCenter; top: parent.top; topMargin: 8; }

            spacing: 8

            Button {
                id: btn_load
                text: "Load"
            }

            Button {
                id: btn_save
                text: "Save"
                onClicked: main.on_btn_save()
            }

            Button {
                id: btn_load_bg
                text: "Load Backdrop"
            }

            Button {
                text: App.backdrop_enable ? "Hide Backdrop" : "Show Backdrop"
                onClicked: App.backdrop_enable = !App.backdrop_enable
            }

            Button {
                text: "Design Mode"
                onClicked: canvas.model.design_mode = true
            }

            Button {
                text: "Sim Mode"
                onClicked: canvas.model.design_mode = false
            }

            Button {
                text: "Add Linear"
                visible: canvas.model.design_mode
                onClicked: canvas.model.scene.add_new_pixel_group("linear")
            }

            /*Button {
                text: "Rectangular"
                visible: canvas.model.design_mode
                onClicked: main.on_btn_add_fixture()
            }

            Button {
                text: "Circular"
                visible: canvas.model.design_mode
                onClicked: main.on_btn_add_fixture()
            }

            Button {
                text: "Arbitrary"
                visible: canvas.model.design_mode
                onClicked: main.on_btn_add_fixture()
            }*/

            Button {
                text: canvas.model.blurred ? "Unblurred" : "Blurred"
                onClicked: canvas.model.blurred = !canvas.model.blurred
            }

            Button {
                text: ((view.visibility == Window.FullScreen) ?
                       "Exit Fullscreen" : "Fullscreen")
                onClicked: {
                    if (view.visibility == Window.FullScreen)
                        view.visibility = Window.Windowed
                    else
                        view.visibility = Window.FullScreen
                }
            }

            Rectangle {
                width: 110
                height: ((canvas.selection.length == 1) ?
                         fixture_info_column.height + 10 :
                         multiple_selection_column.height + 10)
                visible: canvas.model.design_mode && canvas.selection.length > 0

                radius: 5
                color: "#232323"

                Column {
                    id: multiple_selection_column
                    spacing: 4
                    anchors.horizontalCenter: parent.horizontalCenter
                    visible: canvas.selection.length > 1

                    Row {
                        anchors { bottomMargin: 8; topMargin: 24 }
                        Text {
                            font.pixelSize: 14
                            color: "#dddddd"
                            text: canvas.selection.length + " Items Selected"
                        }
                    }
                }

                Column {
                    id: fixture_info_column
                    spacing: 4
                    anchors.horizontalCenter: parent.horizontalCenter
                    visible: canvas.selection.length == 1

                    Row {
                        anchors { bottomMargin: 8; topMargin: 24 }
                        Text {
                            font.pixelSize: 14
                            color: "#dddddd"
                            text: "Pixel Group"
                        }
                    }

                    LabeledInput {
                        id: input_fixture_strand
                        key: "Strand ID"
                        value: canvas.selection.length == 1 ? canvas.selection[0].strand : ""
                    }

                    LabeledInput {
                        id: input_fixture_address
                        key: "Offset"
                        value: canvas.selection.length == 1 ? canvas.selection[0].offset : ""
                    }

                    LabeledInput {
                        id: input_fixture_pixels
                        key: "Pixel Count"
                        value: canvas.selection.length == 1 ? canvas.selection[0].count : ""
                    }
                }
            }
        }
    }
}
