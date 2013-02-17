import QtQuick 1.0

Rectangle {
    id: button

    property alias text: buttonText.text
    property variant action

    color: "#282828"
    width: 110
    height: 32
    radius: 5

    signal clicked

    Rectangle {
        id: shade
        radius: 5
        anchors.fill: button; color: "white"; opacity: 0
    }

    Text {
        id: buttonText
        anchors.centerIn: parent; anchors.verticalCenterOffset: -1
        font.pixelSize: 14
        color: "white"
        smooth: true
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onClicked: {
            if (action != undefined)
                action.trigger()
            parent.clicked()
        }
    }

    states: State {
        name: "pressed"; when: mouseArea.pressed == true
        PropertyChanges { target: shade; opacity: .4 }
    }
}