import QtQuick 1.0
import FireSim 1.0
import "widgets"

Item {
    id: window
    width: 100 //640
    height: 100 //480

    signal backdrop_showhide_callback(variant obj)
    signal labels_showhide_callback(variant obj)
    signal lock_callback(variant obj)
    signal show_center_callback(variant obj)
    signal toggle_blurred_callback(variant obj)

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
        onClicked: {
            window.focus = false;
        }
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
                id: btn_backdrop_showhide
                text: if(main.is_backdrop_enabled()) "Hide Backdrop"; else "Show Backdrop"
                onClicked: backdrop_showhide_callback(btn_backdrop_showhide)
            }

            Button {
                id: btn_labels_showhide
                text: if(main.are_labels_enabled()) "Hide Labels"; else "Show Labels"
                onClicked: labels_showhide_callback(btn_labels_showhide)
            }

            Button {
                id: btn_lock
                text: if(main.is_locked()) "Unlock Scene"; else "Lock Scene"
                onClicked: lock_callback(btn_lock)
            }

            Button {
                id: btn_show_center
                text: if(main.is_center_shown()) "Hide Center"; else "Show Center"
                onClicked: show_center_callback(btn_show_center)
            }

            Button {
                id: btn_toggle_blurred
                text: "Blurred"
                onClicked: toggle_blurred_callback(btn_toggle_blurred)
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