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
        }
    }
}