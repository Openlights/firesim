import QtQuick 2.0
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
                text: "Linear"
                onClicked: main.on_btn_add_fixture()
            }

            Button {
                text: "Rectangular"
                onClicked: main.on_btn_add_fixture()
            }

            Button {
                text: "Circular"
                onClicked: main.on_btn_add_fixture()
            }

            Button {
                text: "Arbitrary"
                onClicked: main.on_btn_add_fixture()
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
                text: App.backdrop_enable ? "Hide Backdrop" : "Show Backdrop"
                onClicked: App.backdrop_enable = !App.backdrop_enable
            }

            Button {
                text: canvas.model.blurred ? "Unblurred" : "Blurred"
                onClicked: canvas.model.blurred = !canvas.model.blurred
            }

            Rectangle {
                width: 110
                height: ((canvas.selection.length == 1) ?
                         fixture_info_column.height + 10 :
                         multiple_selection_column.height + 10)
                visible: canvas.selection.length > 0

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
                        key: "strand"
                        value: main.selected_fixture_strand
                        Binding {
                            target: main
                            property: "selected_fixture_strand"
                            value: input_fixture_strand.value
                        }
                    }

                    LabeledInput {
                        id: input_fixture_address
                        key: "address"
                        value: main.selected_fixture_address
                        Binding {
                            target: main
                            property: "selected_fixture_address"
                            value: input_fixture_address.value
                        }
                    }

                    LabeledInput {
                        id: input_fixture_pixels
                        key: "pixels"
                        value: main.selected_fixture_pixels
                        Binding {
                            target: main
                            property: "selected_fixture_pixels"
                            value: input_fixture_pixels.value
                        }
                    }
                }
            }
        }
    }
}
