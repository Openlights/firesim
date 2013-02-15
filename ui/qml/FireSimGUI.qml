import QtQuick 1.0
import FireSim 1.0
import "widgets"

Item {
    id: window

    width: 640
    height: 480

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

        width: 120
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
                id: btn_load_bg
                text: "Load Backdrop"
            }

            Rectangle {
                width: 100
                height: 150

                radius: 5
                color: "#232323"

                Column {
                    id: fixture_info_column
                    spacing: 8
                    anchors.horizontalCenter: parent.horizontalCenter

                    Text {
                        color: "#dddddd"
                        text: "Fixture Info"
                    }

                    Component {
                        id: fixtureInfoDelegate
                        Item {
                            width: 60
                            height: 20

                            Row {
                                anchors { right: parent.right }
                                anchors { leftMargin: 2; rightMargin: 2 }
                                Text { color: "#eeeeee"; text: key + ": "}
                                Rectangle {
                                    height: 16
                                    width: 25
                                    color: "#444444"
                                    TextInput {
                                        anchors.fill: parent
                                        anchors { leftMargin: 2; rightMargin: 2 }
                                        color: "#eeeeee"
                                        text: value
                                        selectByMouse: true
                                    }
                                }
                            }
                        }
                    }

                    ListView {
                        width: 60
                        height: 80
                        anchors { leftMargin: 2; rightMargin: 2 }
                        model: FixtureInfoModel {}
                        delegate: fixtureInfoDelegate
                    }
                }
            }
        }
    }
}