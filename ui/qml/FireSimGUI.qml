import QtQuick 1.0
import FireSim 1.0
import "widgets"

Item {
    id: window

    width: 640
    height: 480

    signal backdrop_showhide_callback(variant obj)

    MouseArea {
        anchors.fill: parent
        onClicked: window.focus = false;
    }

    SimCanvas {
        id: sim
        anchors {left: toolbox.right; top: parent.top; bottom: parent.bottom; right: parent.right}

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

            Button {
                id: btn_load
                text: "Load Scene"
            }

            Button {
                id: btn_save
                text: "Save Scene"
                onClicked: main.on_btn_save()
            }

            Button {
                id: btn_enable_bg
                text: if(main.is_backdrop_enabled()) "Hide Backdrop"; else "Show Backdrop"
                onClicked: backdrop_showhide_callback(btn_enable_bg)
            }

            Button {
                id: btn_load_bg
                text: "Load Backdrop"
            }

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

                    LabeledInput { key: "id"; value: "" }
                    LabeledInput { key: "strand"; value: "" }
                    LabeledInput { key: "address"; value: "" }
                    LabeledInput { key: "pixels"; value: "" }
                }
            }
        }
    }
}