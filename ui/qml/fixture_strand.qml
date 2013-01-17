import QtQuick 1.0

Rectangle {
    id: fixture

    color: "#0000ff"
    width: 16
    height: 16

    MouseArea {
        id: dragArea
        anchors.fill: parent
        drag.target: fixture
        drag.axis: Drag.XandYAxis
        drag.minimumX: 0
        drag.minimumY: 0
        drag.filterChildren: true

    }
}