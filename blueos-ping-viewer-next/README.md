# BlueOS's Ping Viewer Extension

## Instructions

### Manual Instalation

Access the extensions manager and install with the following parameters.

For Downloadable Extensions, use this manifest URL:

```shell
https://raw.githubusercontent.com/JackSkellet/ping-viewer-next/refs/heads/gh-pages/manifest.json
```

Extensions Manager:

```shell
blueos.local/tools/extensions-manager
```

Parameters:

```shell
jackskellet.ping-viewer-next-discovery-tweak

Ping Viewer 2 Discovery Tweak

Ping-Viewer-Next_Discovery-Tweak

{
  "ExposedPorts": {
    "6060/tcp": {}
  },
  "HostConfig": {
    "Privileged": true,
    "PortBindings": {
      "6060/tcp": [
        {
          "HostPort": ""
        }
      ]
    },
    "NetworkMode": "host"
  }
}
```

### Cockpit Widgets

For each connected ping device, provides a widget accessible through Cockpit as an
[Automatic External Iframe](https://blueos.cloud/cockpit/docs/latest/usage/advanced/#automatic-external-iframes).

Requires BlueOS >= 1.4.
