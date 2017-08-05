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
                id: btn_add_fixture
                text: "Add Fixture"
                onClicked: main.on_btn_add_fixture()
            }

            Button {
                id: btn_clear
                text: "Clear"
                onClicked: main.on_btn_clear()
            }

            /*Button {
                id: btn_load
                text: "Load Scene"
            }*/

            Button {
                id: btn_save
                text: "Save Scene"
                onClicked: main.on_btn_save()
            }

            Button {
                text: App.backdrop_enable ? "Hide Backdrop" : "Show Backdrop"
                onClicked: App.backdrop_enable = !App.backdrop_enable
            }

            Button {
                text: App.labels_visible ? "Hide Labels" : "Show Labels"
                onClicked: App.labels_visible = !App.labels_visible
            }

            Button {
                text: App.locked ? "Unlock Scene" : "Lock Scene"
                onClicked: App.locked = !App.locked
            }

            Button {
                text: App.center_visible ? "Hide Center" : "Show Center"
                onClicked: App.center_visible = !App.center_visible
            }

            Button {
                text: App.blur_enable ? "Unblurred" : "Blurred"
                onClicked: App.blur_enable = !App.blur_enable
            }

            /*Button {
                id: btn_load_bg
                text: "Load Backdrop"
            }*/

            Rectangle {
                width: 110
                height: 150

                radius: 5
                color: "#232323"

                Column {
                    id: fixture_info_column
                    spacing: 4
                    anchors.horizontalCenter: parent.horizontalCenter

                    Row {
                        anchors { bottomMargin: 8; topMargin: 24 }
                        Text {
                            font.pixelSize: 14
                            color: "#dddddd"
                            text: "Fixture Info"
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
