import QtQuick 1.0

Rectangle {
    id: button

    property alias text: buttonText.text
    property variant action

    color: "#282828"
    width: 100
    height: 48

    signal clicked

    Rectangle {
        id: shade
        anchors.fill: button; color: "white"; opacity: 0
    }

    Text {
        id: buttonText
        anchors.centerIn: parent; anchors.verticalCenterOffset: -1
        font.pixelSize: parent.width > parent.height ? parent.height * .25 : parent.width * .25
        style: Text.Sunken; color: "white"; styleColor: "black"; smooth: true
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